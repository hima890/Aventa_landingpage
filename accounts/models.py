from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email or self.username
