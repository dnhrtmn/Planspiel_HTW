from statistics import mode
from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from .filters import *

from . import forms
from . import models


import datetime


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class homeView(generic.TemplateView):
    template_name = "home.html"


def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})


def login_view(request, *args, **kwargs):
    return render(request, "login.html", {})


class user_dashboard(TemplateView):
    template_name = "user_dashboard.html"

    def get_context_data(self, **kwargs):
        if self.request.user.groups.filter(name="stationen").exists():
            context = super(user_dashboard, self).get_context_data(**kwargs)
            # if self.request.user.is_authenticated:
            #     station = int(self.request.user.username[-1:])

            orderData = models.OrderData.objects.all()
            #orderStatus = models.OrderStatus.objects.filter(orderStation=station)
            context['orderData'] = orderData
            #context['orderStatus'] = orderStatus
            return context
        elif self.request.user.groups.filter(name="kunden").exists():
            context = super(user_dashboard, self).get_context_data(**kwargs)
            # if self.request.user.is_authenticated:
            #     station = int(self.request.user.username[-1:])

            orderData = models.OrderData.objects.all()
            #orderStatus = models.OrderStatus.objects.filter(orderStation=station)
            context['customerOrder'] = orderData
            #context['orderStatus'] = orderStatus
            return context


class orderListView(generic.ListView):
    model = models.OrderData
    template_name = "order_list.html"

    # form_class = forms.reservationForm

    # # Filtert die Reservierungen zuerst nach Status des aktuellen Benutzers (Admin oder nicht). Ist der Benutzer ein Admin,
    # # bekommt er alle Reservierungen angezeigt. Ist der Nutzer kein Admin, so bekommt er nur seine Reservierungen angezeigt.
    # # Alle Nutzer haben die Möglichkeiten nach Räumen zu filtern.

    def get_context_data(self, **kwargs):
        #station = int(self.request.user.username[-1:])
        context = super().get_context_data(**kwargs)
        orderData = models.OrderData.objects.all()
        #orderStatus = models.OrderStatus.objects.filter(orderStation=station)
        context['filter'] = orderFilter(
            self.request.GET, queryset=self.get_queryset())
        context['orderData'] = orderData
        #context['orderStatus'] = orderStatus
        return context


class qualityListView(generic.ListView):
    model = models.QualityData
    template_name = "quality_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualityData = models.QualityData.objects.all()
        context['qualityData'] = qualityData
        context['filter'] = qualityFilter(
            self.request.GET, queryset=self.get_queryset())
        return context


class orderStatusListView(generic.ListView):
    model = models.OrderStatus
    template_name = "orderStatus_list.html"

    def get_context_data(self, **kwargs):
        if self.request.user.groups.filter(name="stationen").exists():
            station = int(self.request.user.username[-1:])
            context = super().get_context_data(**kwargs)
            orderStatus = models.OrderStatus.objects.all()
            test = models.OrderStatus.objects.select_related(
                'orderNumber').filter(orderStation=station).filter(orderNumber__id=self.kwargs['pk']).order_by("orderPart")
            context['orderStatus'] = test
            return context
        else:
            context = super().get_context_data(**kwargs)
            orderStatus = models.OrderStatus.objects.all()
            test = models.OrderStatus.objects.select_related(
                'orderNumber').filter(orderNumber__id=self.kwargs['pk']).order_by("orderPart")
            context['orderStatus'] = test
            return context
        # return redirect('/order/status/' + str(kwargs), context)


# View zur Detailansicht einer Bestellung
class orderDetailView(generic.DetailView):
    model = models.OrderData
    template_name = "order_detail.html"
    form_class = forms.orderForm
    pk_url_kwarg = "pk"


# View zum Updaten der Bestellung
class orderUpdateView(generic.UpdateView):
    model = models.OrderData
    template_name = "order_form.html"
    form_class = forms.orderForm
    pk_url_kwarg = "pk"

    def form_valid(self, form):
        return super().form_valid(form)

# View zur Erstellung einer Reservierung inkl. Validierung der Form
# Hier wird auch geprüft ob der User z.B. eine Buchung überbuchen darf oder eine Buchungsanfrage stellen kann


class orderCreateView(generic.CreateView):
    model = models.OrderData
    template_name = "order_form.html"
    form = forms.orderForm

    def get_context_data(self, **kwargs):
        context = super(orderCreateView, self).get_context_data(**kwargs)
        some_data = models.OrderData.objects.all()
        context.update({'some_data': some_data})
        return context
        return render(request, "order_form.html", context)

    def form_valid(self, form):
        return super().form_valid(form)


def createOrder(request):
    form = forms.orderForm()
    if request.method == "POST":
        form = forms.orderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'order_form.html', context)


def startOrder(request, pk, part):
    # station = int(request.user.username[-1:])
    # IF-Funktion zum Abruf des aktuellen OrderStatus

    order = models.OrderData.objects.get(pk=pk)

    orderState = models.OrderStatus.objects.filter(
        orderNumber=pk).filter(id=part).first()

    # print(orderState['orderStatus'])
    # Wenn der Auftragsstatus == NEU ist, dann wird der gesamte sowie die bearbeitende Station(Station1 muss beginnen) auf in Bearbeitung gesetzt
    if order.orderStatus == 'NEW':

        print(1)
        models.OrderStatus.objects.filter(orderNumber=pk).filter(id=part).update(
            orderStatus="PROCESSING", timeBeginn=datetime.datetime.now())
        models.OrderData.objects.filter(pk=pk).update(orderStatus="PROCESSING")
        return redirect('/order/status/' + str(pk))
    # Wenn der Auftragsstatus == in Bearbeitung ist, dann sind weitere Prüfungen notwendig
    elif order.orderStatus == "PROCESSING":

        # Wenn die Nummer der Station der Anzahl der Stationen entspricht (bsp. 6 Station),
        # dann kann der ganze Auftrag beendet werden, andernfalls wird nur die jeweilige Station auf "FINISHED" gesetzt
        if orderState.orderStatus == "NEW":
            print(2)
            models.OrderStatus.objects.filter(orderNumber=pk).filter(id=part).update(
                orderStatus="PROCESSING", timeBeginn=datetime.datetime.now())
            return redirect('/order/status/' + str(pk))
        elif orderState.orderStatus == "PROCESSING":
            print(3)
            print("COUNT", models.Stations.objects.all().count())
            breakpoint()
            if orderState.orderStation == models.Stations.objects.all().count():
                print(4)
                if models.OrderStatus.objects.filter(orderStatus='PROCESSING').count() == 1:
                    models.OrderData.objects.filter(
                        pk=pk).update(orderStatus="FINISHED")
                    models.OrderStatus.objects.filter(orderNumber=pk).filter(id=part).update(
                        orderStatus="FINISHED", timeEnd=datetime.datetime.now())
                    return redirect('/order/status/' + str(pk))
            else:
                print(5)
                models.OrderStatus.objects.filter(orderNumber=pk).filter(id=part).update(
                    orderStatus="FINISHED", timeEnd=datetime.datetime.now())
                return redirect('/order/status/' + str(pk))


def createQualityMsg(request, pk, part):
    form = forms.qualityForm(
        initial={'orderNumber': pk, 'orderPart': part, 'qualityDate': datetime.datetime.now()})
    if request.method == "POST":
        form = forms.qualityForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.orderPart = part
            instance.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'quality_form.html', context)
