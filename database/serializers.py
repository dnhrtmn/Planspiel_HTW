from dataclasses import fields
import imp
from rest_framework import serializers

from .models import OrderData, OrderStatus

class OrderDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderData
        fields = ["orderNumber","quantity","color","screw", "customer", "orderStatus", "orderDate"]

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["orderNumber","orderStation","orderPart","orderBeginn", "orderEnd", "orderStatus"]