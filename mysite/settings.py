import os
from pathlib import Path

# 1. BASE DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY (Keep these secret when selling!)
SECRET_KEY = "django-insecure-1$@d!vuv0$%m@*t-17r0#soy!+=1y*@al7+n^u-zejm!4#$lt*"
DEBUG = True  # Set to False when you officially hand it to the buyer
ALLOWED_HOSTS = ['EmptyBrain.pythonanywhere.com', 'localhost', '127.0.0.1']

# 3. APPLICATION DEFINITION
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "anime", # Your App
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'anime' / 'templates'], 
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# 4. DATABASE (SQLite is perfect for small AI starters)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 5. AUTHENTICATION REDIRECTS
# These ensure the user stays on the search page after login/logout
LOGIN_REDIRECT_URL = 'character_search'
LOGOUT_REDIRECT_URL = 'character_search'
LOGIN_URL = 'login'

# 6. STATIC & MEDIA FILES (Fixed for PythonAnywhere)
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 7. INTERNATIONALIZATION
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
