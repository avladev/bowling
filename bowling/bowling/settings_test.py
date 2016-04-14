from .settings import *

DEBUG = True
TESTING = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}
