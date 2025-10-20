from django.contrib.auth.models import AbstractUser
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    headline = models.CharField(max_length=140, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=120, blank=True)

    # Availability
    is_available_for_hire = models.BooleanField(default=False)
    available_from = models.DateField(blank=True, null=True)
    availability_note = models.CharField(max_length=140, blank=True)

    # Skills
    skills = models.ManyToManyField(Skill, blank=True, related_name='users')

    is_company_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name() or self.username
