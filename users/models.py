import uuid
from django.db import models
from django.contrib.auth.models import User


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"



class TermsVersion(models.Model):
    version = models.CharField(max_length=20, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version


class TermsAcceptance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terms = models.ForeignKey(TermsVersion, on_delete=models.PROTECT)
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "terms")