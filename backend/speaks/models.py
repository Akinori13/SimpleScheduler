from django.db import models

# Create your models here.
class Speak(models.Model):
    content = models.TextField(max_length=140)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20]
