import uuid
import re
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.utils.html import escape
from django.utils.functional import cached_property

_PLACEHOLDER_RE = re.compile(r"\[s*([A-Z_]+)\s*\]")

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"



class TermsVersion(models.Model):
    class Type(models.TextChoices):
        TERMS_OF_SERVICE = "terms_of_service", "Terms of Service"
        PRIVACY_POLICY = "privacy_policy", "Privacy Policy"
        COOKIE_POLICY = "cookie_policy", "Cookie Policy"

    version = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.TERMS_OF_SERVICE)
    content = HTMLField()
    is_active = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now_add=True)

    @cached_property
    def rendered_content(self):
          values = settings.LEGAL_PLACEHOLDERS
          # Unknown tokens are left as they are, so a missing value shows up on the page.
          return _PLACEHOLDER_RE.sub(
              lambda m: escape(values[m[1]]) if values.get(m[1]) else m[0],
              self.content,
          )



    def __str__(self):
        return f"{self.get_type_display()} v{self.version}"


class TermsAcceptance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terms = models.ForeignKey(TermsVersion, on_delete=models.PROTECT)
    version = models.CharField(max_length=20, default="")
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "terms")

class CookieConsent(models.Model):
    """One visitor's cookie choice, kept as proof of consent (GDPR art. 7(1)).

    A new row is written on every choice and never updated. ``consent_id`` is
    the identifier stored in the visitor's consent cookie, so an anonymous
    choice can still be traced back; no IP address is stored.
    """

    consent_id = models.UUIDField(db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    version = models.CharField(max_length=20)
    granted = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cookie consent {self.consent_id} v{self.version}"
