from django.urls import path
from .views import MercadoPagoWebhookView, CrearPreferenciaPagoView, ConfirmarPagoView

urlpatterns = [
    path('webhook/', MercadoPagoWebhookView.as_view(), name='mercadopago_webhook'),
    path('crear-preferencia/', CrearPreferenciaPagoView.as_view(), name='crear_preferencia_pago'),
    path('confirmar-pago/', ConfirmarPagoView.as_view(), name='confirmar_pago'),
]
