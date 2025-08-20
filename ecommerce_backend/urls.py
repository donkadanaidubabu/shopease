from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend and API included from store app
    path('', include('store.urls')),

    # User accounts urls
    path('accounts/', include('accounts.urls')),   # 👈 fixed

    # Cart urls with namespace
    path('cart/', include('cart.urls', namespace='cart')),

    # Chatbot API
    path('api/chatbot/', include('assistantbot.urls')),   # 👈 NEW
]

# Serve media and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
