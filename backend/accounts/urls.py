from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('signup/', views.signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
]
