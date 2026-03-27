from django.db import models


class PageView(models.Model):
    page = models.CharField(max_length=512)
    referrer = models.CharField(max_length=512, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['page']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.page} @ {self.created_at}"
