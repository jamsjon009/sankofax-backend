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
    'django_ckeditor_5',
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
    'apps.blog',
    'apps.connections',
    'apps.community',
    'apps.promotions',
    'apps.analytics',
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
    'apps.core.middleware.PageViewMiddleware',
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
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

# Allow image/document uploads up to 10 MB (avatars, logos, covers, verification docs).
# (nginx client_max_body_size is 20M in prod, so this is the effective limit.)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE

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

# Geocoding (address → lat/lng for the directory map — item #20).
# Provider: 'nominatim' (OpenStreetMap, free, no key) | 'mapbox' | 'none' (disabled).
GEOCODER = env('GEOCODER', default='nominatim')
NOMINATIM_URL = env('NOMINATIM_URL', default='https://nominatim.openstreetmap.org/search')
MAPBOX_TOKEN = env('MAPBOX_TOKEN', default='')

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

# Where to send users after login/logout (default Django value is /accounts/profile/,
# which does not exist in this project and causes a 404 after admin login).
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

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
                    {
                        "title": "Reviews",
                        "icon": "star",
                        "link": "/admin/reviews/review/",
                    },
                ],
            },
            {
                "title": "Admins",
                "separator": True,
                "items": [
                    {
                        "title": "Admin Users",
                        "icon": "admin_panel_settings",
                        "link": "/admin/accounts/adminuserproxy/",
                    },
                ],
            },
            {
                "title": "Companies",
                "separator": True,
                "items": [
                    {
                        "title": "Companies",
                        "icon": "domain",
                        "link": "/admin/profiles/companyprofile/",
                    },
                ],
            },
            {
                "title": "Users",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": "/admin/accounts/regularuserproxy/",
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
                "title": "Blog",
                "separator": True,
                "items": [
                    {
                        "title": "Blog Posts",
                        "icon": "article",
                        "link": "/admin/blog/blogpost/",
                    },
                    {
                        "title": "Blog Categories",
                        "icon": "label",
                        "link": "/admin/blog/blogcategory/",
                    },
                ],
            },
            {
                "title": "Settings",
                "separator": True,
                "items": [
                    {
                        "title": "Site Settings",
                        "icon": "settings",
                        "link": "/admin/core/sitesetting/",
                    },
                    {
                        "title": "Home Content",
                        "icon": "home_app_logo",
                        "link": "/admin/core/homecontent/",
                    },
                    {
                        "title": "Pages",
                        "icon": "description",
                        "link": "/admin/core/page/",
                    },
                    {
                        "title": "FAQs",
                        "icon": "quiz",
                        "link": "/admin/core/faq/",
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
                    {
                        "title": "Testimonials",
                        "icon": "rate_review",
                        "link": "/admin/core/testimonial/",
                        "badge": "apps.core.dashboard.pending_testimonials_badge",
                    },
                ],
            },
        ],
    },
}


# CKEditor 5 config
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'blockQuote', 'code', '|',
            'bulletedList', 'numberedList', '|',
            'insertImage', 'mediaEmbed', '|',
            'insertTable', 'horizontalLine', '|',
            'undo', 'redo',
        ],
        'image': {
            'toolbar': ['imageTextAlternative', 'imageTitle', '|', 'imageStyle:alignLeft', 'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side'],
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells'],
        },
        'height': '400px',
        'width': '100%',
    },
    'minimal': {
        'toolbar': ['bold', 'italic', 'link', 'bulletedList', 'numberedList'],
        'height': '200px',
        'width': '100%',
    },
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'webp']