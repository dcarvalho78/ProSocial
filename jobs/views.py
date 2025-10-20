from rest_framework import viewsets, permissions
from .models import Job
from .serializers import JobSerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related('company').all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
