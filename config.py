import os

DATABASE_NAME = "ranklistener.sqlite"
path = os.path.abspath(os.curdir)


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite://:memory:"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CMC_API_TOKEN = ""
    CMC_BASE_URL = ""

    TG_BOT_TOKEN = ""
    TG_WEBHOOK = ""

    RESULT_COUNT = 10


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://user@localhost/foo"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}/{DATABASE_NAME}"
    CMC_API_TOKEN = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
    CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

    TG_BOT_TOKEN = "1966936694:AAGWO8DX-3d1iTCfejjS_tJBiDeAVd7trXs"
    TG_WEBHOOK = "https://coinmarketcaplistener.herokuapp.com/"

    RESULT_COUNT = 10


class TestingConfig(Config):
    TESTING = True
