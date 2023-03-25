from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email or Username"

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s or email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # check if username is actually an email address
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                pass
            else:
                if user.check_password(password):
                    self.cleaned_data['username'] = user.username

        return super().clean()
