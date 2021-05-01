from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('home/', views.HomeView.as_view(), name='home'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/update', views.ProfileUpdateView.as_view(), name='profile_update'),
]
