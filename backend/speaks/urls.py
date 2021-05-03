from django.urls import path
from . import views

app_name = 'speaks'
urlpatterns = [
    path('new/', views.SpeakCreateView.as_view(), name='speak_create'),
]
