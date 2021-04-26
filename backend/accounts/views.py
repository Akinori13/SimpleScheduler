from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from .models import User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:signup')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

class HomeView(LoginRequiredMixin, generic.TemplateView):
    template_name="accounts/home.html"
