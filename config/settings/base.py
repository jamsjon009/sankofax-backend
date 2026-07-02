from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

DJANGO_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'storages',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.profiles',
    'apps.directory',
    'apps.reviews',
    'apps.subscriptions',
    'apps.crm',
    'apps.events',
    'apps.marketplace',
    'apps.newsletter',
    'apps.core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres:postgres@localhost:5432/sankofax')
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SankofaX API',
    'DESCRIPTION': 'Global Black & African Business Directory — SankofaX',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = True

STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@sankofax.com')

FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

UNFOLD = {
    "SITE_TITLE": "SankofaX",
    "SITE_HEADER": "SankofaX",
    "SITE_SUBHEADER": "CRM & Admin",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "home",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Directory",
                "separator": True,
                "items": [
                    {
                        "title": "Listings",
                        "icon": "storefront",
                        "link": "/admin/directory/listing/",
                        "badge": "apps.core.dashboard.pending_listings_badge",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/directory/category/",
                    },
                    {
                        "title": "Amenities",
                        "icon": "checklist",
                        "link": "/admin/directory/amenity/",
                    },
                ],
            },
            {
                "title": "Users & Companies",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "Company Profiles",
                        "icon": "business",
                        "link": "/admin/profiles/companyprofile/",
                    },
                    {
                        "title": "Reviews",
                        "icon": "star",
                        "link": "/admin/reviews/review/",
                    },
                ],
            },
            {
                "title": "Subscriptions",
                "separator": True,
                "items": [
                    {
                        "title": "Plans",
                        "icon": "workspace_premium",
                        "link": "/admin/subscriptions/plan/",
                    },
                    {
                        "title": "Subscriptions",
                        "icon": "receipt_long",
                        "link": "/admin/subscriptions/subscription/",
                    },
                ],
            },
            {
                "title": "CRM",
                "separator": True,
                "items": [
                    {
                        "title": "Leads",
                        "icon": "person_add",
                        "link": "/admin/crm/lead/",
                    },
                    {
                        "title": "Support Tickets",
                        "icon": "support_agent",
                        "link": "/admin/crm/supportticket/",
                    },
                ],
            },
            {
                "title": "Marketing",
                "separator": True,
                "items": [
                    {
                        "title": "Newsletter",
                        "icon": "mail",
                        "link": "/admin/newsletter/subscriber/",
                    },
                    {
                        "title": "Events",
                        "icon": "event",
                        "link": "/admin/events/event/",
                    },
                    {
                        "title": "Marketplace",
                        "icon": "shopping_bag",
                        "link": "/admin/marketplace/product/",
                    },
                ],
            },
        ],
    },
}
