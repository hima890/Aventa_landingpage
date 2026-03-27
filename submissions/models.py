from django.db import models


class WaitlistSubmission(models.Model):
    full_name = models.CharField(max_length=255)
    whatsapp = models.CharField(max_length=30)
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    main_problem = models.TextField()
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['business_type']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.full_name} – {self.business_name}"
