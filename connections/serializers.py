from rest_framework import serializers
from .models import Connection

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id','from_user','to_user','status','created_at']
