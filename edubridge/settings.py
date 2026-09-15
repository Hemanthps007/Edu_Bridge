import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env, falling back to .env.example if .env is missing
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(BASE_DIR / '.env.example')
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-edubridge-dev-key-change-in-prod-2026')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,.vercel.app')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]

if os.getenv('VERCEL') == '1' or os.getenv('VERCEL_URL'):
    if '.vercel.app' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('.vercel.app')
    vercel_url = os.getenv('VERCEL_URL')
    if vercel_url and vercel_url not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(vercel_url)

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()])

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edubridge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'edubridge.wsgi.application'

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY', '')

# Serverless / Vercel Environment Detection
IS_VERCEL = bool(
    os.getenv('VERCEL') == '1'
    or os.getenv('VERCEL') == 'true'
    or os.getenv('VERCEL_URL')
    or os.getenv('VERCEL_ENV')
    or os.getenv('AWS_LAMBDA_FUNCTION_NAME')
)

# Dual database configuration: SQLite for local/demo/tests, Supabase PostgreSQL when valid SUPABASE_DB_URL or DATABASE_URL provided
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
if db_url and db_url.startswith(('postgresql://', 'postgres://')):
    try:
        import importlib
        dj_db_url = importlib.import_module("dj_database_url")
        DATABASES = {
            'default': dj_db_url.parse(
                db_url,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True
            )
        }
    except Exception:
        import urllib.parse as urlparse
        url = urlparse.urlparse(db_url)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:] if url.path else 'postgres',
                'USER': url.username or 'postgres',
                'PASSWORD': url.password or '',
                'HOST': url.hostname,
                'PORT': url.port or 5432,
                'OPTIONS': {
                    'sslmode': 'require',
                }
            }
        }
else:
    # On serverless (Vercel / Lambda), BASE_DIR is read-only; use /tmp for SQLite fallback
    sqlite_path = Path('/tmp/db.sqlite3') if IS_VERCEL else (BASE_DIR / 'db.sqlite3')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_path,
        }
    }

# Session Management: signed cookies for serverless / Vercel to avoid read-only filesystem errors
if IS_VERCEL:
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    SESSION_FILE_PATH = BASE_DIR / '.sessions'
    try:
        SESSION_FILE_PATH.mkdir(exist_ok=True)
    except OSError:
        SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 86400 * 7

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase_credentials.json')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
SITE_NAME = os.getenv('SITE_NAME', 'EduBridge')

CORS_ALLOW_ALL_ORIGINS = DEBUG
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
