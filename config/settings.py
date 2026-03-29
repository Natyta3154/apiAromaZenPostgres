import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# 🔐 SEGURIDAD
# =========================
SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ["apiaromazenpostgres.onrender.com", "127.0.0.1", "localhost"]

# =========================
# 🌐 CORS (para Vercel)
# =========================
CORS_ALLOWED_ORIGINS = [
    "https://front-aroma-zen-postgres.vercel.app",  # CAMBIAR por tu URL real
]
CSRF_TRUSTED_ORIGINS = [
    "https://front-aroma-zen-postgres.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True


#Render usa proxy → Django a veces se confunde
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# =========================
# 📦 APPS
# =========================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    'apps.usuarios',
    'apps.productos',
    'apps.carrito',
    'apps.pagos',
    'apps.blog',
    'apps.comentarios',
    'apps.pedidos',
    'apps.super',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # podés agregar templates globales acá si querés
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

# =========================
# 🐘 BASE DE DATOS (Render)
# =========================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

DATABASES['default']['sslmode'] = 'require'

# =========================
# 🔑 DJANGO REST + JWT
# =========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# =========================
# 📊 SWAGGER
# =========================
SPECTACULAR_SETTINGS = {
    'TITLE': 'AromaZen API',
    'DESCRIPTION': 'API de AromaZen',
    'VERSION': '1.0.0',
}

# =========================
# 💳 MERCADOPAGO
# =========================
MERCADOPAGO_ACCESS_TOKEN = config('MP_ACCESS_TOKEN', default='')

# =========================
# 🌍 INTERNACIONALIZACIÓN
# =========================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# =========================
# 📁 STATIC FILES
# =========================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# 🔐 AUTH
# =========================
AUTHENTICATION_BACKENDS = [
    'apps.usuarios.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]