from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        # When an user tries to recreate his/her new account with same email, delete the account, which is registerd with the email.
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
