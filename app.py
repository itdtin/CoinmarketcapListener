import atexit
import re

import telegram
from telegram import ParseMode
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from coinmarketcap.cmc_client import Coinmarketcap
from core.logger.logger import logger
from ranking.ranking import Ranking
from telebot.telegram_utils import create_table_to_send, define_query_params


app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)

global bot
global TOKEN
TOKEN = app.config.get("TG_BOT_TOKEN")
logger.error(f"token {TOKEN}")
bot = telegram.Bot(token=TOKEN)

with app.app_context():
    from db.cmc_entities_models import Currency, RankHistorical

    db.create_all()
    rank_listener = Coinmarketcap(
        app.config.get("CMC_BASE_URL"), app.config.get("CMC_API_TOKEN"), db
    )
    rank_listener.fill_cmc_data()
migrate = Migrate(app, db)


sched = BackgroundScheduler(daemon=True, timezone="UTC")
# sched.add_job(sensor, "interval", seconds=10)
sched.add_job(
    rank_listener.fill_cmc_data, trigger="cron", hour="0"
)  # Run every day at 0:00:00
sched.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


if __name__ == "__main__":

    app.run(threaded=True)
