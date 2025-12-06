from dotenv import load_dotenv

from os import getenv
from pathlib import Path
from random import choices
from string import ascii_letters

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LIVE_DEBUG = getenv("LIVE_DEBUG", False)
DOMAIN = getenv("DOMAIN", None)
SECRET_KEY = getenv("DJANGO_SECRET", "".join(choices(ascii_letters, k=128)))

if DOMAIN:
    DEBUG = LIVE_DEBUG
    ALLOWED_HOSTS = [f"{DOMAIN}", "127.0.0.1", "localhost"]
    ADMIN_URL = "/api/admin"
    CSRF_TRUSTED_ORIGINS = [f"https://{DOMAIN}"]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", "host.docker.internal"]

# Database env vars - postgres
DB_HOST = getenv("DB_HOST", None)
DB_PORT = getenv("DB_PORT", "5432")
DB_USER = getenv("DB_USER", "")
DB_PASS = getenv("DB_PASS", "")
DB_NAME = getenv("DB_NAME", "moonseacodex")

# Database env vars - sqlite
DB_PATH = Path(getenv("DB_PATH", BASE_DIR))

# EMail env vars
EMAIL_API_KEY = getenv("EMAIL_API_KEY")
DEFAULT_EMAIL_SENDER = getenv("DEFAULT_EMAIL_SENDER")


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "discord_auth",
    "codex",
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

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "core.wsgi.application"

if DB_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASS,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DB_PATH / "msc-db.sqlite3",
        },
    }

AUTH_USER_MODEL = "codex.CodexUser"
AUTHENTICATION_BACKENDS = [
    "discord_auth.auth.DiscordAuthenticationBackend",
    "codex.utils.backends.CustomUserModelBackend",
]
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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "codex.utils.security.SessionCSRFExemptAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}

# ############################################################################### #
#                          Settings for discord authentication
# ############################################################################### #

DISCORD_CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET", "")
DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID", "")

AUTH_COMPLETE_URL = getenv("OAUTH_COMPLETE_URL", "")
AUTH_REDIRECT_URL = getenv("OAUTH_REDIRECT_URL", "")
AUTH_FAIL_URL = getenv("OAUTH_FAIL_URL", "")

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
APPEND_SLASH = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "admin_static/"
STATIC_ROOT = BASE_DIR / "admin_static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_HOST = "smtp.sendgrid.net"
DEFAULT_FROM_EMAIL = DEFAULT_EMAIL_SENDER
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = EMAIL_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
