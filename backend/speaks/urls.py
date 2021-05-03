from django.urls import path, include
from . import views

app_name = 'speaks'
urlpatterns = [
    path('new/', views.SpeakCreateView.as_view(), name='speak_create'),
]
