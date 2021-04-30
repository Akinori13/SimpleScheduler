from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic

from .forms import CustomUserCreationForm
from .models import Profile

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

class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    fields = ['text', 'icon_image', 'header_image']
    template_name = 'accounts/profile_update.html'
    context_object_name = 'profile'
    
    def get_success_url(self):
        return reverse('accounts:profile_detail', args=[self.kwargs['pk']])
