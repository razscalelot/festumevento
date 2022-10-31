"""
Django settings for festumevento_api project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sco#if&^m&u&i5vhu$rf8d1n(73k7752ll8)rfftv)1o2+q15@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
# CORS_ALLOWED_ORIGINS = [
#     "http://127.0.0.1:8000",
#     "http://192.168.29.223:8080",
#     "http://localhost:4200",
# ]
# CORS_ALLOWED_ORIGINS = True

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:4200",
    "http://192.168.29.223:8080"
]

# Application definition

FCM_SERVER_API_KEY = "AAAAa6V4Q_E:APA91bFt4XJd_U75F_cEw-cPOiOREVx7fs99m6JHJHeIMXJaqcPN-8F04V8-Q2aRcYNN27BpC-N3qb1JiH51q6TjRZqblZY-4YzgGlpH8H0mb4ubAN4QktVuD31Co4MWPuf1_JcgUISW"
INSTALLED_APPS = [
    "sslserver",
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'rest_auth',
    'crispy_forms',
    'api',
    'sales',
    'chatterbot.ext.django_chatterbot',
    'corsheaders',
    'channels',
    "twilio",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'festumevento.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

CHATTERBOT = {
    'name': 'Test',
    'logic_adapters': [
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter',
        'chatterbot.logic.BestMatch'
    ]
}

AUTH_USER_MODEL = 'users.User'
WSGI_APPLICATION = 'festumevento.wsgi.application'
ASGI_APPLICATION = 'festumevento.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_AUTH_SERIALIZERS = {
    'TOKEN_SERIALIZER': 'users.serializers.TokenSerializer',
}
SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}


MEDIA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/'
print(MEDIA_ROOT)
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
# --------------Local-------------------
# DATABASES = {
#     'default':
#         {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'festumevento1',
#             'USER': 'root',
#             'PASSWORD': "root",
#             'HOST': "localhost",
#             'PORT': "3306",
#             'OPTIONS': {
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#             }
#         }
# }

# ---------------Production----------------
# DATABASES = {
#     'default':
#         {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'festumevento_uat',
#             'USER': 'main',
#             'PASSWORD': "Nomorob@32",
#             'HOST': "139.59.90.124",
#             'PORT': "3306",
#             'OPTIONS': {
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#             }
#         }
# }

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'festumevento_uat',
            'USER': 'ubuntu',
            'PASSWORD': "",
            'HOST': "localhost",
            'PORT': "3306",
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        }   
}

# --------------Scalelot-----------------------
# DATABASES = {
#     'default':
#         {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'festumevento_uat',
#             'USER': 'festumevento_user',
#             'PASSWORD': 'festumevento_p',
#             'HOST': "localhost",
#             'PORT': "3306",
#             'OPTIONS': {
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#             }
#         }
# }

# DOCKER CONFIGRATIONS
# DATABASES = {
#     'default':
#         {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'festumevento_uat',
#             'USER': 'root',
#             'PASSWORD': "root",
#             'HOST': "192.168.29.223",
#             'PORT': "5555",
#             'OPTIONS': {
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#             }
#         }
# }

# --------------UAT-----------------------
# DATABASES = {
#     'default':
#         {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'festumevento_uat',
#             'USER': 'admin',
#             'PASSWORD': 'admin_festo_2019',
#             'HOST': "festumevento.cjqyfwsbjzdy.ap-south-1.rds.amazonaws.com",
#             'PORT': "3306",
#             'OPTIONS': {
#                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#             }
#         }
# }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CRISPY_TEMPLATE_PACK = "bootstrap4"
LOGIN_REDIRECT_URL = "/salespanel/home"
LOGOUT_REDIRECT_URL = "/salespanel/home"
# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'raj.scalelot@gmail.com'
EMAIL_HOST_PASSWORD = 'gvmtexrozjcjevdw'
EMAIL_USE_TLS = True
