from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReseñaViewSet, MensajeContactoCreateView

router = DefaultRouter()
router.register(r'', ReseñaViewSet, basename='reseña')

urlpatterns = [
    path('contacto/', MensajeContactoCreateView.as_view(), name='enviar-contacto'),
    path('', include(router.urls)),
]
