from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms_accepted = forms.BooleanField(
        required=True,
        initial=False,
        label=(
            "I confirm that I am at least 18 years old and that I have read "
            "and accept the Terms and Conditions."
        ),
        error_messages={
            "required": (
                "You must confirm that you are at least 18 years old and accept "
                "the Terms and Conditions."
            )
        },
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass
