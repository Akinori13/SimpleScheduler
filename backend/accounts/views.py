from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView
from django.template.loader import render_to_string

from libraries.authentications import OnlyAnonymousUserMixin
from .forms import CustomUserCreationForm
from .models import Profile, User
from speaks.models import Speak

class SignupView(OnlyAnonymousUserMixin, CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(str(user.pk)),
            'user': user
        }
        subject = render_to_string('registration/signup_subject.txt', context)
        message = render_to_string('registration/signup_email.html', context)
        user.email_user(subject, message)
        return redirect('accounts:signup_done')


class SignupDoneView(OnlyAnonymousUserMixin, TemplateView):
    template_name = 'registration/signup_done.html'


class SignupCompleteView(OnlyAnonymousUserMixin, TemplateView):
    template_name = 'registration/signup_complete.html'
    max_age = settings.ACTIVATION_TIMEOUT_SECONDS

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.max_age)
        except SignatureExpired:
            return HttpResponseBadRequest()
        except BadSignature:
            return HttpResponseBadRequest()
        except Exception as e:
            return HttpResponseBadRequest()
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                    user = User.objects.get(pk=user_pk)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return super().get(request, **kwargs)
        return HttpResponseBadRequest()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "accounts/home.html"
    queryset = Speak.objects.order_by('-created_at')
    paginate_by = 4
    context_object_name = 'speaks'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/settings.html'


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['text', 'icon_image', 'header_image']
    template_name = 'accounts/profile_update.html'
    context_object_name = 'profile'
    
    def get_success_url(self):
        return reverse(
            'accounts:profile_detail', 
            args=[self.kwargs['pk']]
            )
