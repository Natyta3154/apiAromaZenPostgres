from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticuloViewSet, testimonios

router = DefaultRouter()
router.register(r'posts', ArticuloViewSet, basename='articulo')

urlpatterns = [
    path('', include(router.urls)),
    path('testimonios/', testimonios, name='blog_testimonios'),
]
