import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'comments',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': '127.0.0.1',
    }
}

ALLOWED_HOSTS = ['testserver', "127.0.0.1"]
