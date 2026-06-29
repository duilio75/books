from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, LoginForm
from .models import EmailVerificationToken, TermsVersion, TermsAcceptance


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

        token_obj = EmailVerificationToken.objects.create(user=user)
        _send_verification_email(request, user, token_obj)

        return redirect("verify_email_sent")

    return render(request, "users/register.html", {"form": form})


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
    return render(request, "users/dashboard.html")



def terms_view(request):
    latest = TermsVersion.objects.filter(is_active=True).first()

    if request.method == "POST":
        TermsAcceptance.objects.get_or_create(
            user=request.user,
            terms=latest,
            defaults={
                "ip_address": request.META.get("REMOTE_ADDR")
            }
        )
        return redirect("/")

    return render(request, "users/terms.html", {"terms": latest})
