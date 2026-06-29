from django.shortcuts import redirect
from .models import TermsVersion, TermsAcceptance

class TermsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.path.startswith("/terms")
            and not request.path.startswith("/logout")
            and not request.path.startswith("/admin")
        ):
            latest = TermsVersion.objects.filter(is_active=True).first()

            if latest and not TermsAcceptance.objects.filter(
                user=request.user,
                terms=latest
            ).exists():
                return redirect("terms")

        return self.get_response(request)