from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet

router = DefaultRouter()
router.register(r'lista', ProductoViewSet, basename='producto')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

urlpatterns = [
    path('destacados/', ProductoViewSet.as_view({'get': 'destacados'}), name='producto-destacados'),
    path('', include(router.urls)),
]
