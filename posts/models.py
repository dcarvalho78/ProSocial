from django.db import models
from django.conf import settings
from companies.models import Company

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post({self.author} {'@'+self.company.name if self.company else ''})"
