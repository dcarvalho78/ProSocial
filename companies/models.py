from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='companies/logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='companies/banners/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='managed_companies', blank=True)
    employees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='employers', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
