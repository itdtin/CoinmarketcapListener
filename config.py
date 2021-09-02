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

    RESULT_COUNT = 100


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = "ranklistener.sqlite"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    print(SQLALCHEMY_DATABASE_URI)
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}/{DATABASE_NAME}"
    CMC_API_TOKEN = os.environ.get("CMC_API_TOKEN")
    CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

    TG_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TG_WEBHOOK = "https://cmclistener.herokuapp.com/"

    RESULT_COUNT = 10


class TestingConfig(Config):
    TESTING = True
