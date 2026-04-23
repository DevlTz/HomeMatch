from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = ["*"]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "apps.users",
    "apps.properties",
    "apps.search",
    "apps.ai_analysis",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

CORS_ALLOW_ALL_ORIGINS = True

# Cloudflare R2
# Default to None so the app starts without R2 in local dev.
# AiVisionClient / boto3 will raise at the point of first use if unset.
R2_ACCESS_KEY_ID = config("R2_ACCESS_KEY_ID", default=None)
R2_ACCOUNT_ID = config("R2_ACCOUNT_ID", default=None)
R2_SECRET_ACCESS_KEY = config("R2_SECRET_ACCESS_KEY", default=None)
R2_BUCKET_NAME = config("R2_BUCKET_NAME", default=None)
# Storage backend
# Set USE_LOCAL_STORAGE=True in .env to skip Cloudflare R2 and serve
# files from MEDIA_ROOT instead. For development only.
USE_LOCAL_STORAGE = config("USE_LOCAL_STORAGE", default=False, cast=bool)

# AI Vision API
# Default to None; AiAnalysisService validates and raises ValueError on first
# instantiation if these are missing, keeping the error surface narrow.
AI_API_BASE_URL = config("AI_API_BASE_URL", default="https://generativelanguage.googleapis.com/v1beta/openai/")
AI_API_KEY = config("AI_API_KEY", default=None)
AI_MODEL = config("AI_MODEL", default="gemini-3-flash-preview")
# Default analysis prompt
# Centralised here so it can be overridden per-environment without touching code.
# Accepts a custom prompt for future use cases.
AI_ANALYSIS_DEFAULT_PROMPT = config(
    "AI_ANALYSIS_DEFAULT_PROMPT",
    default=(
        "Analyze this property photo and return subjective atributes accordingly."
        "Consider: brightness (if sun shines through the windows or the walls have a darker saturation are factors to take into consideration for 'brightness'), architectural style (strictly follow this list: Colonial (Portuguese), Baroque, Rococo (limited), Neoclassical, Eclectic, Art Nouveau (rare), Art Deco, Early Modern (proto-modernism), Modernist (Brazilian modernism), Tropical modernism, Brutalist, Postmodern, Contemporary, Vernacular (regional), Vernacular coastal (praiano), Neo-colonial, Neo-classical revival, Minimalist, High-rise modern (urban residential/commercial), Gated-community suburban (condomínio fechado style)),"
        "furniture quality and style (by the amount of art pieces, the property receives an 'artsy' value, if the furniture is abundant, it receives a high 'furniture_amount' value, and if this furniture is modern or vintage it receives 'modern' and 'vintage' values), overall atmosphere (if it is comfortable, as in 'cozy'; if it has lots of plants and other natural elements, 'verdant';  if the space looks well utilized, 'spacious'; if the place looks dirty, 'clean'; if the place has 'warm' colors or 'cold' colors; if the place has lots of windows or other crevices, 'ventilation'), "
        "and the apparent age of the property (if it looks recently renovated or well maintained, it receives a 'new' value, if it looks old or in need of repairs, it receives an 'old' value) as well as the age of the style of the property (if it looks like a style that was popular in the last 20 years, it receives a 'contemporary' value, if it looks like a style that was popular between 20 and 50 years ago, it receives a 'classic' value, and if it looks like a style that was popular more than 50 years ago, it receives a 'historic' value, and if it looks like something from the future or avant-garde, it receives a 'futuristic' value)."
        "Return only the attributes in the requested structured format, without additional text."
    ),
)
