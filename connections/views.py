from rest_framework import viewsets, permissions
from .models import Connection
from .serializers import ConnectionSerializer

class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.select_related('from_user','to_user').all().order_by('-created_at')
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.AllowAny]
