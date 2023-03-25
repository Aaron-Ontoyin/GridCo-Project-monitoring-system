from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            # check if username is actually an email address
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # username is not an email address, try to authenticate as usual
            user = super().authenticate(request, username=username, password=password, **kwargs)
        else:
            # username is an email address, check the password
            if user.check_password(password):
                return user

        return None
