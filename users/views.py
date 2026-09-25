import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm
from .cookies import category_keys, read_consent, write_consent
from .models import CookieConsent, EmailVerificationToken, TermsVersion
from .terms import (
    active_required_documents,
    outstanding_documents,
    record_acceptance,
)


def _send_verification_email(request, user, token_obj):
    verification_url = request.build_absolute_uri(f"/verify-email/{token_obj.token}/")
    send_mail(
        subject="Confirm your email address",
        message=(
            f"Hi {user.username},\n\n"
            f"Please click the link below to verify your email address:\n\n"
            f"{verification_url}\n\n"
            "If you did not create an account, you can ignore this email."
        ),
        from_email=None,  # uses DEFAULT_FROM_EMAIL from settings
        recipient_list=[user.email],
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        ip_address = request.META.get("REMOTE_ADDR")
        for document in active_required_documents():
            record_acceptance(user, document, ip_address)

        token_obj = EmailVerificationToken.objects.create(user=user)
        _send_verification_email(request, user, token_obj)

        return redirect("verify_email_sent")

    return render(request, "users/register.html", {"form": form})


def terms_view(request):
    """Public Terms & Conditions page, rendered from the active TermsVersion."""
    terms = TermsVersion.objects.filter(
        type=TermsVersion.Type.TERMS_OF_SERVICE, is_active=True
    ).first()

    return render(request, "users/terms.html", {"terms": terms})



def policy_view(request):
    """Privacy Policy page, rendered from the active PrivacyPolicy."""
    terms = TermsVersion.objects.filter(
        type=TermsVersion.Type.PRIVACY_POLICY, is_active=True
    ).first()
    return render(request, "users/policy.html", {"terms": terms})




def cookie_policy_view(request):
    """Cookie Policy page, with the form to change cookie preferences."""
    terms = TermsVersion.objects.filter(
        type=TermsVersion.Type.COOKIE_POLICY, is_active=True
    ).first()
    return render(request, "users/cookie_policy.html", {"terms": terms})


@require_POST
def cookie_consent_view(request):
    """Store the visitor's cookie choice from the banner or preferences form.

    Works as a plain form post (redirects back to ``next``) and, for the
    banner's JS, as a fetch returning JSON.
    """
    action = request.POST.get("action")
    if action == "accept_all":
        granted = category_keys()
    elif action == "reject_all":
        granted = []
    else:
        chosen = set(request.POST.getlist("categories"))
        granted = [key for key in category_keys() if key in chosen]

    previous = read_consent(request)
    consent_id = previous["id"] if previous else uuid.uuid4()
    CookieConsent.objects.create(
        consent_id=consent_id,
        user=request.user if request.user.is_authenticated else None,
        version=settings.COOKIE_CONSENT_VERSION,
        granted=granted,
    )

    if "application/json" in request.headers.get("Accept", ""):
        response = JsonResponse({"granted": granted})
    else:
        next_url = request.POST.get("next", "")
        if not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            next_url = "/"
        response = redirect(next_url)
    write_consent(response, consent_id, granted)
    return response




def verify_email_sent_view(request):
    return render(request, "users/verify_email_sent.html")


def verify_email_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()

    login(request, user)
    return redirect("dashboard")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get("next", "dashboard")
        return redirect(next_url)

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard_view(request):
    outstanding = outstanding_documents(request.user)
    return render(request, "users/dashboard.html", {
        "terms_accepted": not outstanding,
        "outstanding_terms": outstanding,
    })


@login_required
def accept_terms_view(request):
    if request.method != "POST":
        return redirect("dashboard")

    outstanding = outstanding_documents(request.user)
    submitted = set(request.POST.getlist("accepted_types"))
    if any(document.type not in submitted for document in outstanding):
        messages.error(
            request, "Please accept every document listed in order to continue."
        )
        return redirect("dashboard")

    if outstanding:
        ip_address = request.META.get("REMOTE_ADDR")
        for document in outstanding:
            record_acceptance(request.user, document, ip_address)
        messages.success(request, "Thanks for accepting our conditions!")
    return redirect("dashboard")
