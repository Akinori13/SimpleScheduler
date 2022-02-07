from email.policy import default
from django.db import models

# Create your models here.
class Scraping(models.Model):
    name = models.CharField(
        max_length=30
    )
    description = models.TextField(
        max_length=140
    )
    codes = models.JSONField(
        default=dict
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
