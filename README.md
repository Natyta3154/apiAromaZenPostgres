# AromaZen - E-commerce de Sahumerios 🌿

AromaZen es una plataforma de e-commerce moderna y escalable construida con **Django** y **Django REST Framework**. El proyecto está enfocado en la venta de productos de aromaterapia, con un sistema modular que incluye gestión de productos, carrito de compras, integración de pagos con Mercado Pago y un sistema de blog/comentarios.

##🚀 Características Principales

- **Autenticación Segura**: Implementación de JWT (JSON Web Tokens) para una comunicación segura entre frontend y backend.
- **Catálogo de Productos**: Gestión completa de categorías y productos con validaciones de stock.
- **Carrito de Compras**: Sistema persistente para gestionar la selección de productos de los usuarios.
- **Pasarela de Pagos**: Integración con la API de Mercado Pago para procesar transacciones.
- **Blog y Comunidad**: Espacio para artículos informativos y sistema de comentarios para interacción con usuarios.
- **API RESTful**: Endpoints organizados y documentados para facilitar el consumo desde cualquier cliente (React, Vue, Mobile, etc.).

## 🛠️ Stack Tecnológico

- **Backend**: Django 5.x + Django REST Framework.
- **Base de Datos**: PostgreSQL.
- **Autenticación**: SimpleJWT.
- **Pagos**: Mercado Pago SDK.
- **Otros**: CORS Headers para integración con frontend.

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular para facilitar la escalabilidad:

```text
App-Zahumeri-postgres/
├── apps/               # Aplicaciones del proyecto
│   ├── usuarios/       # Gestión de cuentas y perfiles
│   ├── productos/      # Catálogo y categorías
│   ├── carrito/        # Gestión de compras temporales
│   ├── pagos/          # Integración con Mercado Pago
│   ├── blog/           # Artículos y contenido
│   └── comentarios/    # Sistema de feedback
├── config/             # Configuración central (urls, settings, wsgi)
├── manage.py           # Herramienta de gestión de Django
└── venv/               # Entorno virtual (excluido de Git)
```

## ⚙️ Configuración e Instalación

### Requisitos Previos

- Python 3.10+
- PostgreSQL
- Git

### Pasos para el Setup

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/App-Zahumeri-postgres.git
   cd App-Zahumeri-postgres
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   # Windows
   python -m venv venv
   .\venvApi\Scripts\Activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**:
   Asegúrate de tener PostgreSQL corriendo y crea una base de datos llamada `ecommerce_db`. Puedes ajustar las credenciales en `config/settings.py` o usar variables de entorno.

5. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

6. **Crear un superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Iniciar el servidor**:
   ```bash
   python manage.py runserver
   ```

## 📖 Uso de la API

La API está disponible en los siguientes prefijos de ruta:

- **Autenticación**: `/api/auth/`
- **Productos**: `/api/productos/`
- **Carrito**: `/api/carrito/`
- **Administración**: `/admin/`

## 📖 Documentación Interactiva (Swagger) 🚀

Para facilitar el desarrollo y las pruebas, este proyecto utiliza **drf-spectacular** para generar documentación automática:

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) (Recomendado para pruebas interactivas).
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/) (Vista de lectura limpia).
- **Esquema JSON**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/).

Desde el **Swagger UI**, puedes probar cada endpoint directamente sin necesidad de herramientas externas como Postman.

---
*Desarrollado para brindar la mejor experiencia en aromaterapia.* ✨

crear el requirements.txt

pip freeze > requirements.txt

gunicorn config.wsgi:application