"""
Django settings for checkmate project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import django_permissions_policy
import yaml

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BASE_DIR.parent

secrets_path = PROJECT_DIR / 'SECRETS.yaml'
if secrets_path.is_file():
    with open(secrets_path, 'rt') as f:
        SECRETS = yaml.safe_load(f)
else:
    SECRETS = {}
extension_manifest_path = PROJECT_DIR / 'checkmate-extension' / 'manifest.json'
if extension_manifest_path.is_file():
    with open(extension_manifest_path, 'rt') as f:
        EXTENSION_VERSION = json.load(f)['version']
else:
    EXTENSION_VERSION = None


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Make sure this gets set to a non-default value.
SECRET_KEY = SECRETS.get('SECRET_KEY')
if SECRET_KEY is None:
    logger.warning('Using a default secret key')
    SECRET_KEY = 'k-Mmzuzy882vG6Captio-0yDNLjDW4ijBAkc_lBC39DHfQq8seyfEKzcqUoPWt904hJ-V0W-Cf45bMbQxc1fqg'


# Trust Reverse Proxy. This is dangerous if used without one.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ORIGIN = os.environ.get('SERVER_ORIGIN', 'https://localhost')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = 6379

ALLOWED_HOSTS = [
    '.localhost',
    '127.0.0.1',
    '[::1]',
    urlparse(ORIGIN).hostname,
]

# Application definition
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'checkmate',
    'structure',
    'accounts',
    'services',
    'django.contrib.postgres',
    'django_extensions',
    'django_admin_hstore_widget',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'cachalot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'checkmate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


ASGI_APPLICATION = 'checkmate.asgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'HOST': POSTGRES_HOST,
        'USER': 'postgres',
        'PASSWORD': 'postgres',
    }
}

class REDIS_DATABASE_ENUM:
    CACHE = 1
    CELERY = 2
    REDIS_CLIENT = 3

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE_ENUM.CACHE}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
        },
    },
}


# Auth

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = None
ACCOUNT_ADAPTER = 'accounts.admin.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.admin.SocialAccountAdapter'

SITE_ID = 1

DRIVE_SETTINGS = SECRETS.get('DRIVE_SETTINGS', {})
if 'credentials_file' in DRIVE_SETTINGS:
    with open(PROJECT_DIR / DRIVE_SETTINGS['credentials_file'], 'rt') as f:
        DRIVE_SETTINGS['credentials'] = json.load(f)
if 'oauth' in DRIVE_SETTINGS:
    # Google OAuth uses the secret but not the key field, but it needs to exist
    DRIVE_SETTINGS['oauth']['key'] = ''
DISCORD_CREDENTIALS = SECRETS.get('DISCORD_CREDENTIALS', {})

SOCIALACCOUNT_PROVIDERS = {
    'discord': {
        'SCOPE': ['identify'],
        'APP': DISCORD_CREDENTIALS,
    },
    'google': {
        'SCOPE': [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
        'APP': DRIVE_SETTINGS.get('oauth', {}),
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# API Auth
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
DEFAULT_AUTHENTICATION_CLASSES = [
    'rest_framework.authentication.SessionAuthentication',
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

FRONTEND_DIR = PROJECT_DIR / 'frontend'
BACKEND_DIR = BASE_DIR
STATICFILES_DIRS = [
    os.path.join(BACKEND_DIR, 'static'),
    '/build/frontend/static',
]
STATIC_ROOT = '/build/backend/static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ROOT = os.path.join(BACKEND_DIR, 'static_root')

# External services configuration
# allow all as if they were root document
PERMISSIONS_POLICY = {
    feature: '*' for feature in django_permissions_policy.FEATURE_NAMES
}

# Celery
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE_ENUM.CELERY}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE_ENUM.CELERY}'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 5 * 60,
}
CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULE = {
    'auto_create_new_puzzles': {
        'task': 'services.tasks.auto_create_new_puzzles',
        'kwargs': {
            'dry_run': False,
            'manual': False,
        },
        'schedule': 30.0, # every 30 seconds
        'options': {
            'expires': 20.0,
        },
    },
}
