from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from . import views
from . import api

router = routers.DefaultRouter()
router.register("OrderData", api.orderDataViewSet)
router.register("OrderStatus", api.orderStatusViewSet)

urlpatterns = [
    #path('', views.index, name='index'),
    path("", views.user_dashboard.as_view(), name='user_dashboard'),
    path("order/", views.orderListView.as_view(), name="order_list"),
    path("order/status/<int:pk>", views.orderStatusListView.as_view(),
         name="orderStatus_list"),
    path("order/create/", views.createOrder, name="order_create"),
    path("order/detail/<int:pk>/",
         views.orderDetailView.as_view(), name="order_detail"),
    path("order/update/<int:pk>/",
         views.orderUpdateView.as_view(), name="order_update"),
    #path("order/delete/<int:pk>/", views.orderDeleteView.as_view(), name="order_delete"),
    path("order/start/<int:pk>/<int:part>",
         views.startOrder, name="order_start"),
    #path('login/', views.login_view, name='login'),
    path('', include('django.contrib.auth.urls')),
    path("api/v1/", include(router.urls)),
    path("order/quality/create/<int:pk>/<int:part>",
         views.createQualityMsg, name="quality_create"),
    path("order/quality/detail/<int:pk>/<int:part>",
         views.qualityDetailView.as_view(), name="quality_detail"),
    path("order/quality/update/<int:pk>/<int:part>",
         views.qualityUpdateView.as_view(), name="quality_update"),
    path("order/quality/list", views.qualityListView.as_view(), name="quality_list"),
    path("order/quality/process/<int:pk>/<str:state>",
         views.qualityProcess, name="quality_process")

]
