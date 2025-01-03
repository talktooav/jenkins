import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yma(makt47u(1$evuu4vdbs_4arh+*!k)qqc!ht(%)@qdtz*8c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True 

ALLOWED_HOSTS = ['127.0.0.1', '52.66.228.107']

# Application definition

INSTALLED_APPS = [
    'django_crontab',
    'django_cron',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users',
    'roles',
    'account',
    'jobrole',
    'jobusers',
    'quiz',
    'postcategory',
    'post',
    'userentity',
    'pushNotification',
    'moderation',
    'rewards',
    'americanaStore',
    'widget_tweaks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'americana.middleware.CurrentSlugMiddleware',
]

ROOT_URLCONF = 'americana.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.media',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'americana.context_processor.all_brands',
                'americana.context_processor.subdomain_slug',
                'americana.context_processor.base_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'americana.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'americana',
        'USER': 'amrc_user',
        'PASSWORD': 'Neuro@1009!@#',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGOUT_REDIRECT_URL = '/login'
BASE_URL = 'http://52.66.228.107:8080'


AUTH_USER_MODEL    = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = (
    # ... your other backends
    'django.contrib.auth.backends.ModelBackend',
    'account.auth_backend.PasswordlessAuthBackend',
)

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES' : ('rest_framwork.permission.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ]
}
# ~ POINTS_ON_ACTIONS = {"new_post":35,"comment":25,"like":10,"gif_comment":10}

STATIC_URL = '/static/'

STATICFILES_DIRS = [
  os.path.join(BASE_DIR, "assets"),
]
# ~ STATUS = {'0' : 'Inactive', '1' : 'Active'}
STATIC_ROOT = os.path.join(os.path.join(BASE_DIR), 'static_cdn')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "static_cdn", "upload_media")

CRON_CLASSES = [
    'account.cron.MyCronJob'
]
# ~ import time
# ~ CRONJOBS = [
# ~ ('01 00 * * *', 'account.cron.add_user_birthday_cron_job', '>> /root/crons/response'+time.strftime("%Y%m%d-%H%M%S")+'.log')
    # ~ ('0 1 * * *', 'account.crons.add_user_birthday_cron_job'),
# ~ ]
