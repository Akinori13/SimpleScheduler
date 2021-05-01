from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        help_text='こちらのEmailは後から変更できます。',
        required=False
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

