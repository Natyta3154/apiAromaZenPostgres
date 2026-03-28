"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,)
    
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.usuarios.views import CustomTokenObtainPairView, RegistroUsuarioView, UsuarioMeView, health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación (JWT)
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtener'),
    path('api/auth/refrescar/', TokenRefreshView.as_view(), name='token_refrescar'),
    
    # También incluimos registro y me en el bloque de auth para que coincida con la guía
    path('api/auth/registro/', RegistroUsuarioView.as_view(), name='registro_usuario_auth'),
    path('api/auth/me/', UsuarioMeView.as_view(), name='perfil_usuario_auth'),
    
    # Esquema y Documentación de API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Utilidades y Salud
    path('api/health/', health_check, name='health_check'),

    # Rutas de las Aplicaciones
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/productos/', include('apps.productos.urls')),
    path('api/carrito/', include('apps.carrito.urls')),
    path('api/pagos/', include('apps.pagos.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/comentarios/', include('apps.comentarios.urls')),
]
