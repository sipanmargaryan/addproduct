import os
from datetime import timedelta

from .base import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.str('SECRET_KEY', 'Keep it secret!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.bool('DEBUG', True)
ENABLE_DEBUG_TOOLBAR = DEBUG and ENV.bool('ENABLE_DEBUG_TOOLBAR', False)

ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', [])
INTERNAL_IPS = ENV.list('INTERNAL_IPS', default=('127.0.0.1', ))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
]

EXTERNAL_APPS = [
    'django_celery_results',
    'widget_tweaks',
    'django_extensions',
    'channels',
    'storages',
    'ckeditor',
    'ckeditor_uploader',
    'mptt',
    'paypal.standard.ipn',
    'django_filters',
    'rest_framework',
    'corsheaders',
    'rest_framework_swagger',
    'compressor',
]

PROJECT_APPS = [
    'core',
    'ads',
    'common',
    'users',
    'messaging',
    'faq',
    'events',
    'payments',
    'blog',
]

INSTALLED_APPS.extend(EXTERNAL_APPS + PROJECT_APPS)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'project.middleware.BasicAuthMiddleware',
]

# Django Debug Toolbar settings
# https://django-debug-toolbar.readthedocs.io/en/stable/configuration.html

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

    DEBUG_TOOLBAR_CONFIG = {
        'RESULTS_CACHE_SIZE': 50,
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.sql.SQLPanel',
    ]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.routing.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': ENV.db_url('DATABASE_URL', default='sqlite://:memory:'),
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ('en', ugettext('English')),
    ('ar', ugettext('Arabic')),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'collectstatic')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_ENABLED = ENV.bool('COMPRESS_ENABLED', False)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST API settings

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 15,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

API_VERSION = 1


# Redis settings
REDIS_URL = 'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_PATH}'.format(
    REDIS_HOST=ENV.str('REDIS_HOST', '127.0.0.1'),
    REDIS_PORT='6379',
    REDIS_PATH='0',
)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Celery settings
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TASK_ALWAYS_EAGER = ENV.bool('CELERY_TASK_ALWAYS_EAGER', False)

CELERY_ROUTES = {
    'accounts.tasks.AsyncEmailTask': {'queue': 'accounts'},
}

# Admin settings

ADMIN_EMAIL = 'admin@example.com'

# Email settings
DEFAULT_FROM_EMAIL = 'sipanmmargaryan@gmail.com'
EMAIL_BASE_TEMPLATE = 'email/base.html'
EMAIL_HOST = ENV.str('EMAIL_HOST', 'localhost')
EMAIL_PORT = ENV.int('EMAIL_PORT', 25)
EMAIL_BACKEND = ENV.str('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST_USER = 'sipanmmargaryan@gmail.com'
EMAIL_HOST_PASSWORD = 'masaha2019'
EMAIL_USE_TLS = True

# User settings

AUTH_USER_MODEL = 'users.User'

# Social Auth

SOCIAL_GOOGLE_KEY = ENV.str('SOCIAL_GOOGLE_KEY')
SOCIAL_GOOGLE_SECRET = ENV.str('SOCIAL_GOOGLE_SECRET')
SOCIAL_TWITTER_CONSUMER_KEY = ENV.str('SOCIAL_TWITTER_CONSUMER_KEY')
SOCIAL_TWITTER_CONSUMER_SECRET = ENV.str('SOCIAL_TWITTER_CONSUMER_SECRET')
SOCIAL_FACEBOOK_KEY = ENV.str('SOCIAL_FACEBOOK_KEY')
SOCIAL_FACEBOOK_SECRET = ENV.str('SOCIAL_FACEBOOK_SECRET')
SOCIAL_INSTAGRAM_KEY = ENV.str('SOCIAL_INSTAGRAM_KEY')
SOCIAL_INSTAGRAM_SECRET = ENV.str('SOCIAL_INSTAGRAM_SECRET')

# Site settings

SITE_NAME = ENV.str('SITE_NAME', 'Masaha')
CLIENT_DOMAIN = ENV.str('CLIENT_DOMAIN', '127.0.0.1:8000')
URL_SCHEME = ENV.str('URL_SCHEME', 'http')
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Basic Auth

ENABLE_HTTP_BASIC_AUTH = ENV.bool('ENABLE_HTTP_BASIC_AUTH', False)
HTTP_BASIC_AUTH = {
    'masaha': 'masaha2019',
}
HTTP_BASIC_AUTH_EXCLUDE_URLS = (
    '/paypal/'
)

# S3 Storage

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = ENV.str('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = ENV.str('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = ENV.str('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Paypal

PAYPAL_RECEIVER_EMAIL = ENV.str('PAYPAL_RECEIVER_EMAIL', None)
PAYPAL_TEST = ENV.str('PAYPAL_IS_TEST_MODE', True)

# KNET

KNET_API_KEY = ENV.str('KNET_API_KEY', None)

# Google

GOOGLE_API_KEY = ENV.str('GOOGLE_API_KEY', None)
GOOGLE_ANALYTICS_ID = ENV.str('GOOGLE_ANALYTICS_ID', None)

# Editor settings

CKEDITOR_UPLOAD_PATH = 'blog/'
AWS_QUERYSTRING_AUTH = False

# Mailchimp settings

MAILCHIMP_API_KEY = ENV.str('MAILCHIMP_API_KEY', None)
MAILCHIMP_LIST_ID = ENV.str('MAILCHIMP_LIST_ID', None)

# Firebase Cloud Messaging

FCM_SERVER_KEY = ENV.str('FCM_SERVER_KEY', None)

# Currency conversion settings

FIXER_KEY = ENV.str('FIXER_KEY', None)

# Sentry DSN

SENTRY_DSN = ENV.str('SENTRY_DSN', None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
