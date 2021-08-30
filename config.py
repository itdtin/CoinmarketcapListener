import os


path = os.path.abspath(os.curdir)


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite://:memory:"
    DATABASE_NAME = "ranklistener.sqlite"
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
    DATABASE_NAME = "ranklistener.sqlite"
    SQLALCHEMY_DATABASE_URI = "postgresql://jhxhmlfrsczmpq:ce76286c7fb921f72a8ac5853855b9cdfcc4ca35b28a20194eae6d10443a639e@ec2-52-208-221-89.eu-west-1.compute.amazonaws.com:5432/d9hsqa8jsotu37"
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}/{DATABASE_NAME}"
    CMC_API_TOKEN = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
    CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

    TG_BOT_TOKEN = "1966936694:AAGWO8DX-3d1iTCfejjS_tJBiDeAVd7trXs"
    TG_WEBHOOK = "https://cmclistener.herokuapp.com/"

    RESULT_COUNT = 10


class TestingConfig(Config):
    TESTING = True
