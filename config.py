import os


path = os.path.abspath(os.curdir)


class Config:
    DEBUG = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    CMC_API_TOKEN = os.environ.get("CMC_API_TOKEN")
    CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

    TG_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TG_WEBHOOK = "https://cmclistener.herokuapp.com/"

    RESULT_COUNT = 10
    ROTATE_PERIOD = 365  # count of days
