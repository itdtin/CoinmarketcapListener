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
from routes.telegram_routes import telegram_routes


app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
app.register_blueprint(telegram_routes)

global bot
global TOKEN


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


@app.route("/")
def hello_world():
    data = Ranking.get_top_gainers(
        engine=db.engine, count_result=app.config.get("RESULT_COUNT"), days=5
    )
    return str(data)


@app.route("/setwebhook", methods=["GET", "POST"])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook(
        "{URL}{HOOK}".format(URL=app.config.get("TG_WEBHOOK"), HOOK=TOKEN)
    )
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


if __name__ == "__main__":

    app.run(threaded=True)
