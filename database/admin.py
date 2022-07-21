from django.contrib import admin

# Register your models here.

from .models import OrderData, OrderStatus, QualityData, Stations, Customer, GameRound

admin.site.register(OrderData)
admin.site.register(OrderStatus)
admin.site.register(QualityData)
admin.site.register(Stations)
admin.site.register(Customer)
admin.site.register(GameRound)