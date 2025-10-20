from rest_framework import serializers
from .models import User, Skill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','headline','bio','location',
                  'is_available_for_hire','available_from','availability_note','skills','is_company_admin']
