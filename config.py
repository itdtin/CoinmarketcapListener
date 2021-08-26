import os

DATABASE_NAME = "ranklistener.sqlite"
path = os.path.abspath(os.curdir)


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite://:memory:"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://user@localhost/foo"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}/{DATABASE_NAME}"


class TestingConfig(Config):
    TESTING = True
