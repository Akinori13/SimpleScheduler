from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('speaks/', include('speaks.urls')),
    path('video/', include('video.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

