import os
from pathlib import Path
from datetime import timedelta

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad (¡Cambiar en producción!)
SECRET_KEY = 'django-insecure-tu-clave-secreta-aqui'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Intentar cargar variables de entorno desde .env manualmente
ENV_FILE = BASE_DIR / '.env'
print(f"--- Buscando archivo .env en: {ENV_FILE} ---")

if ENV_FILE.exists():
    print("✅ Archivo .env encontrado.")
    with open(ENV_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                try:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    
                    os.environ[key] = val
                    
                    if key == "MP_ACCESS_TOKEN":
                        # Usamos una variable temporal y un slice explícito [0:10]
                        # para ayudar al verificador de tipos (Pylance/Pyright)
                        token_preview = val[0:10]
                        print(f"Token cargado (inicia con): {token_preview}...")
                except (ValueError, IndexError):
                    continue
else:
    print("Archivo .env NO encontrado.")

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]



# para ngrok pruebas en local
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "dihydroxy-adultly-necole.ngrok-free.dev",
]
MERCADOPAGO_WEBHOOK_URL = "https://dihydroxy-adultly-necole.ngrok-free.dev/api/pagos/webhook/"
FRONTEND_URL = "http://localhost:5173"




CORS_ALLOW_CREDENTIALS = True

# Definición de Aplicaciones
INSTALLED_APPS = [
    'jazzmin',  # Jazzmin debe ir antes de django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías Externas
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # Aplicaciones del Proyecto (Estructura Modular)
    'apps.usuarios',
    'apps.productos',
    'apps.carrito',
    'apps.pagos',
    'apps.blog',
    'apps.comentarios',
    'apps.pedidos',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Manejo de CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Configuración de Base de Datos para PostgreSQL
# Nota: Ajustar credenciales según entorno
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecommerce_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuración de API Documentation (Swagger/OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'AromaZen API',
    'DESCRIPTION': 'Documentación técnica de la API de AromaZen (Sahumerios & Aromaterapia).',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'defaultModelRendering': 'model',
        'displayRequestDuration': True,
    },
}

# Configuración de JWT (SimpleJWT)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Configuración de Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')

if not MERCADOPAGO_ACCESS_TOKEN or MERCADOPAGO_ACCESS_TOKEN == 'TEST-YOUR-ACCESS-TOKEN':
    # En desarrollo, si no hay token, podrías querer un aviso
    print("\n  ADVERTENCIA: No se ha detectado un MP_ACCESS_TOKEN válido en las variables de entorno.")

# Internacionalización (Idioma Español)
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de Usuario Personalizado (Opcional pero recomendado)
# AUTH_USER_MODEL = 'usuarios.Usuario'

# Backends de Autenticación (Dual: Email o Username)
AUTHENTICATION_BACKENDS = [
    'apps.usuarios.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Configuración de Jazzmin (Admin Moderno)
JAZZMIN_SETTINGS = {
    "site_title": "AromaZen Admin",
    "site_header": "AromaZen",
    "site_brand": "AromaZen - Esencia & Armonía",
    "welcome_sign": "Bienvenido al Panel de Gestión de AromaZen",
    "copyright": "AromaZen Ltd",
    "search_model": ["auth.User", "productos.Producto"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Soporte", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"},
        {"app": "productos"},
    ],
    "usermenu_links": [
        {"name": "Soporte", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "apps.usuarios": "fas fa-users",
        "apps.productos.Producto": "fas fa-spa",
        "apps.productos.Categoria": "fas fa-tags",
        "apps.blog.Articulo": "fas fa-pen-nib",
        "apps.comentarios.Reseña": "fas fa-star",
        "apps.carrito.Carrito": "fas fa-shopping-cart",
        "apps.pagos.Pago": "fas fa-credit-card",
    },
    "order_with_respect_to": ["auth", "usuarios", "productos", "blog", "comentarios", "carrito", "pagos"],
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_patch_scroll": False,
    "sidebar_theme": "sidebar-dark-primary",
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
