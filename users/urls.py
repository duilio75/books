from django.urls import path
from . import views

urlpatterns = [
    path("signin", views.login_view, name="signin"),
    path("signup", views.register_view, name="signup"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("verify-email/sent", views.verify_email_sent_view, name="verify_email_sent"),
    path("verify-email/<uuid:token>/", views.verify_email_view, name="verify_email"),
    path("terms", views.terms_view, name="terms"),
]
