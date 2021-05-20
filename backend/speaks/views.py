from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import DeleteView

from .models import Speak

class SpeakCreateView(LoginRequiredMixin, CreateView):
    model = Speak
    fields = ['content']
    template_name = 'speaks/speak_create.html'
    success_url = reverse_lazy('accounts:home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class SpeakDeleteView(LoginRequiredMixin, DeleteView):
    model = Speak
    template_name = 'speaks/speak_delete.html'
    success_url = reverse_lazy('accounts:home')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
