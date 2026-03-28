from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticación que permite al usuario ingresar con email o username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Buscamos todos los usuarios que coincidan por username o email
        users = User.objects.filter(Q(username=username) | Q(email=username))
        
        for user in users:
            # Verificamos la contraseña para cada uno de los posibles matches
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
