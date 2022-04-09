from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from .models import Speak

class SpeakListView(ListView):
    model = Speak
    context_object_name = 'speaks'
    template_name = 'speaks/speak_list.html'


class SpeakCreateView(LoginRequiredMixin, CreateView):
    model = Speak
    fields = ['content']
    template_name = 'speaks/speak_create.html'
    success_url = reverse_lazy('accounts:home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SpeakReadView(DetailView):
    model = Speak
    template_name = 'speaks/speak_read.html'
    context_object_name = 'speak'


class SpeakUpdateView(LoginRequiredMixin, UpdateView):
    model = Speak
    fields = ['content']
    template_name = 'speaks/speak_update.html'
    success_url = reverse_lazy('accounts:home')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class SpeakDeleteView(LoginRequiredMixin, DeleteView):
    model = Speak
    template_name = 'speaks/speak_delete.html'
    success_url = reverse_lazy('accounts:home')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
