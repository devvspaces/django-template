
import atexit
from pathlib import Path
from decouple import config
import logging_loki
import structlog
from multiprocessing import Queue

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


APP_TAG = config('APP_TAG', default='django-app')
SECRET_KEY = config('SECRET_KEY', default='django-insecure-avw@xz#v1d9wgn@2cw1zp%!b!&cp04$(27qvs$kr0^fd(4h3i@')
DJ_ENV = config('DJ_ENV', default='development')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Plugins
    "django_structlog",
    # 'django_celery_results',
    
    # Apps
    'authapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "django_structlog.middlewares.RequestMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DB_TYPE = config("DB_TYPE", default="sqlite3")
if DB_TYPE == "sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {
                "timeout": 100,
            }
        }
    }
if DB_TYPE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
        }
    }


# REDIS
REDIS_URL = config("REDIS_URL", default=None)

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }


# Email

EMAIL_HOST = config("EMAIL_HOST", default=None)
EMAIL_PORT = config("EMAIL_PORT", default=None)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=None)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=None)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=None)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=None)
    


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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
  BASE_DIR / "assets",
]
STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MAX_IMAGE_UPLOAD_SIZE=1000

AUTH_USER_MODEL = 'authapp.User'

LOGIN_REDIRECT_URL = 'dashboard:home'
LOGIN_URL = 'auth:login'

# Configure Loki settings
LOKI_HOST = config("LOKI_HOST", default="http://localhost:3100")  # Change to your Loki instance URL
LOKI_URL = f"{LOKI_HOST}/loki/api/v1/push"  # Change to your Loki instance URL
LOKI_AUTH = None  # Set to (username, password) if authentication is required
LOKI_TAGS = {
    "application": APP_TAG,
    "environment": DJ_ENV,
    "host": "server-1",           # Hostname or server identifier
}


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create Loki queue handler
loki_handler = logging_loki.LokiQueueHandler(
    Queue(-1),  # Use unlimited queue size
    url=LOKI_URL,
    auth=LOKI_AUTH,
    tags=LOKI_TAGS,
    version="1",
)

# Register shutdown handler to ensure logs are flushed on exit
def ensure_logs_flushed():
    loki_handler.flush()


atexit.register(ensure_logs_flushed)

# Logging
LOG_PATH = BASE_DIR / "logs"
LOG_PATH.mkdir(exist_ok=True)
LOGLEVEL = config("LOGLEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "app_log": {
            "handlers": ["console", 'json_file', "loki"],
            "level": LOGLEVEL,
        },
        'django.db.backends': {
            'handlers': ["console", 'json_file', "loki"],
            'level': LOGLEVEL,
            'propagate': False,
        },
        "django": {
            "handlers": ["console", 'json_file', "loki"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", 'json_file', "loki"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", 'json_file', "loki"],
            "level": "INFO",
            "propagate": False,
        },
        "": {  # Root logger
            "handlers": ["console"],
            "level": "INFO",
        },
    },
    "handlers": {
        "loki": {
            "()": lambda: loki_handler,  # Use our pre-configured handler
            "formatter": "json_formatter",
            "level": LOGLEVEL,
        },
        "json_file": {
            "level": LOGLEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_PATH / "app.log",
            "formatter": "json_formatter",
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,      # Keep 5 backup files
        },
        'console': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'plain_console',
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} : {asctime} : {message}",
            "style": "{",
        },
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
            ],
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
        },
    },
}

# Configure django-structlog
DJANGO_STRUCTLOG_CELERY_ENABLED = False  # Set to True if using Celery


CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = REDIS_URL
CELERY_TIMEZONE = "Australia/Tasmania"