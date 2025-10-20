from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id','company','title','description','location','employment_type','salary_min','salary_max','created_at']
