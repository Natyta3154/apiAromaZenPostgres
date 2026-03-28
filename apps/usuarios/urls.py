from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistroUsuarioView, UsuarioMeView, CustomTokenObtainPairView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login_token'),
    path('refrescar/', TokenRefreshView.as_view(), name='token_refrescar'),
    path('me/', UsuarioMeView.as_view(), name='perfil_usuario'),
]
