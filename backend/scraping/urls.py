from django.urls import path

from . import views

app_name = 'scraping'
urlpatterns = [
    path('', views.ScrapingHomeView.as_view(), name='home'),
    path('create', views.ScrapingCreateView.as_view(), name='create_scraping'),
]
