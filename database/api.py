from rest_framework import viewsets, permissions

from . import serializers
from . import models


class orderDataViewSet(viewsets.ModelViewSet):
    """ViewSet for the OrderData class"""

    queryset = models.OrderData.objects.all()
    serializer_class = serializers.OrderDataSerializer
    permission_classes = [permissions.IsAuthenticated]


class orderStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for the OrderStatus class"""

    queryset = models.OrderStatus.objects.all()
    serializer_class = serializers.OrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]