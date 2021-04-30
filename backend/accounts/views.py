from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from .models import Profile, User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

def signup(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

class HomeView(LoginRequiredMixin, generic.TemplateView):
    template_name="accounts/home.html"

class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'
