
from django.contrib import admin
from django.urls import path, include
from api import views

from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView)

urlpatterns = [
    path('', views.login, name='home'),
    path('admin/', admin.site.urls),
    path('oauth/', views.login, name='login'),
    path('accounts/login/', views.google_login, name='google_login'),
    path('accounts/google/login/callback/',
         views.google_callback, name='google_callback'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('api/', include('api.urls')),
    path('api/v1/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("profile/", views.ProfileView.as_view(), name="profile"),
]
