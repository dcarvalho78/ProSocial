from django.db import models
from django.conf import settings

class Connection(models.Model):
    PENDING = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'
    STATUS_CHOICES = [(PENDING,'Pending'),(ACCEPTED,'Accepted'),(REJECTED,'Rejected')]
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connections_sent')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connections_received')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user','to_user')

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.get_status_display()})"
