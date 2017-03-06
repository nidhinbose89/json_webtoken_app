import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '@#$23456super-secret-key3456&*'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=300)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(seconds=600)


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True