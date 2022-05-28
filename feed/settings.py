"""
Django settings for feed project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
from corsheaders.defaults import default_headers as default_cors_headers

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "heheejeeje")
HULSE_LANDING_URL = os.environ.get("HULSE_LANDING_URL", "https://hulse.app/")
HULSE_DASHBOARD_URL = os.environ.get(
    "HULSE_DASHBOARD_URL", "https://dashboard.hulse.app/"
)
HULSE_DESKTOP_URL = os.environ.get("HULSE_DESKTOP_URL", "http://localhost:4240/")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "channels",
    "django_eventstream",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "feedapp",
    "social_django",
    "django.contrib.humanize",
    "rest_framework",
    "rest_framework.authtoken",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}


SITE_ID = 1
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_cors_headers) + ["metadata", "Content-Disposition"]
CORS_EXPOSE_HEADERS = ["metadata", "Content-Disposition"]


MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_grip.GripMiddleware",
]


ROOT_URLCONF = "feed.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "feed.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# NOTE: automatically forwarded to postgresql in prod
DB_NAME = os.environ.get("DB_NAME", "db.sqlite3")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / DB_NAME,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


AUTH_USER_MODEL = "feedapp.User"

# Auth0 settings
SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
SOCIAL_AUTH_AUTH0_DOMAIN = os.environ.get("SOCIAL_AUTH_AUTH0_DOMAIN")
SOCIAL_AUTH_AUTH0_KEY = os.environ.get("SOCIAL_AUTH_AUTH0_KEY")
SOCIAL_AUTH_AUTH0_SECRET = os.environ.get("SOCIAL_AUTH_AUTH0_SECRET")

SOCIAL_AUTH_AUTH0_SCOPE = ["openid", "profile", "email"]

AUTHENTICATION_BACKENDS = {
    "social_core.backends.auth0.Auth0OAuth2",
    "django.contrib.auth.backends.ModelBackend",
}

LOGIN_URL = "login"  #'/login/auth0'
LOGIN_REDIRECT_URL = "callback"
# LOGOUT_REDIRECT_URL = '/'

SUPPORTED_TASKS = [
    "summarization",
    "translation",
    "text-generation",
    "text-classification",
    "sentiment-analysis",
    "question-answering",
    "text2text-generation",
    "zero-shot-classification",
]

# django event stream related stuff
ASGI_APPLICATION = "feed.asgi.application"
EVENTSTREAM_STORAGE_CLASS = "django_eventstream.storage.DjangoModelStorage"
EVENTSTREAM_CHANNELMANAGER_CLASS = "feedapp.channelmanager.ChannelAuthManager"

# whitenoise related stuff
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# CSRF_TRUSTED_ORIGINS = [
#    "http://localhost:8000",
#    "https://hulse-api.herokuapp.com/",
#    "https://hulse-api.herokuapp.com",
# ]

# handle heroku
import django_on_heroku

django_on_heroku.settings(locals())
