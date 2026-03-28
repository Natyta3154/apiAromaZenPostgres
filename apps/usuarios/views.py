from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.db import connection
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegistroUsuarioSerializer, 
    UsuarioSerializer, 
    CustomTokenObtainPairSerializer
)

class RegistroUsuarioView(generics.CreateAPIView):
    """
    Vista para registrar un nuevo usuario en el sistema.
    """
    queryset = User.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para el login que devuelve datos extra del usuario.
    """
    serializer_class = CustomTokenObtainPairSerializer

class UsuarioMeView(APIView):
    """
    Devuelve los datos del usuario autenticado actualmente.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Verifica la salud del sistema (Conexión a BD).
    """
    health_status = {
        "status": "healthy",
        "database": "connected",
        "message": "AromaZen API is running smoothly."
    }
    try:
        connection.ensure_connection()
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return Response(health_status, status=503)
    
    return Response(health_status)
