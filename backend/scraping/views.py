from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy

from .models import Scraping


class ScrapingHomeView(LoginRequiredMixin, TemplateView):
    template_name = "scraping/home.html"


class ScrapingCreateView(LoginRequiredMixin, CreateView):
    model = Scraping
    fields = ['name', 'description', 'codes']
    template_name = 'scraping/scraping_create.html'
    success_url = reverse_lazy('scraping:home')
