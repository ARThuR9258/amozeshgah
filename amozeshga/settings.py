"""
Django settings for amozeshga project.
مقادیر حساس و محیطی از فایل .env خوانده می‌شوند.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


def _env_list(name: str, default: str = '') -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(',') if x.strip()]


# --- امنیت و محیط ---

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-only-change-in-production',
)

DEBUG = _env_bool('DEBUG', True)

ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

CSRF_TRUSTED_ORIGINS = _env_list('CSRF_TRUSTED_ORIGINS')

# --- اپلیکیشن ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'index_module.apps.IndexModuleConfig',
    'django_render_partial',
    'account_module',
    'sample_questions',
    'rest_framework',
    'quizbuilder_module',
    'subscriptions_module',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'amozeshga.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'index_module.context_processors.dashboard_sidebar',
            ],
        },
    },
]

WSGI_APPLICATION = 'amozeshga.wsgi.application'

# --- دیتابیس (PostgreSQL) ---

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'amozeshgah_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
    }
}

# --- احراز هویت ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'account_module.User'

AUTHENTICATION_BACKENDS = [
    'account_module.backends.PhoneNumberBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
}

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Tehran')
USE_I18N = True
USE_TZ = True

# --- فایل‌های استاتیک (CSS/JS) ---

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
            if not DEBUG
            else 'django.contrib.staticfiles.storage.StaticFilesStorage'
        ),
    },
}

# --- فایل‌های آپلود (تصاویر سوال و ...) ---

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', str(BASE_DIR / 'media')))

# در production تصاویر را nginx سرو می‌کند؛ در dev از Django
SERVE_MEDIA = _env_bool('SERVE_MEDIA', DEBUG)

# --- production ---

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', True)
    CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE', True)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

LOGIN_URL = '/account/sign-in/'
LOGIN_REDIRECT_URL = 'first_page'
