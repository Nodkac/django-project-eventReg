"""
Django settings for campus project.
Production-ready for PythonAnywhere + local dev friendly.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# Core
# ------------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    # OK for demos; for real projects set SECRET_KEY in the PA "Environment variables"
    "dev-only-secret-key-change-me"
)

# Local dev defaults to True; in PythonAnywhere set DJANGO_DEBUG=False (recommended) or leave as is here.
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

# Allow local and your PA domain
PA_DOMAIN = os.getenv("PA_DOMAIN", "<your-username>.pythonanywhere.com")
ALLOWED_HOSTS = ["127.0.0.1", "localhost", PA_DOMAIN]

# Required for secure POSTs from your PA domain (must be https)
CSRF_TRUSTED_ORIGINS = [f"https://{PA_DOMAIN}"]

# ------------------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "events",
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

ROOT_URLCONF = "campus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],   # app templates auto-discovered
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "campus.wsgi.application"

# ------------------------------------------------------------------------------
# Database
# Using SQLite file for PythonAnywhere and local by default
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static files
# PA: collectstatic will place files here; map /static/ to this dir in the Web tab
# ------------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------------------------------------------------
# Misc
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Dev-only email backend (prints emails to console). Safe in prod; swap later if needed.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
