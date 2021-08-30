import atexit
import re

import telegram
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from coinmarketcap.cmc_client import Coinmarketcap
from core.logger.logger import logger
from ranking import Ranking


def sensor():
    """ Function for test purposes. """

    rank_listener.fill_cmc_data()


sched = BackgroundScheduler(daemon=True, timezone="UTC")
sched.add_job(sensor, "interval", days=1)
sched.start()


app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
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


@app.route("/")
def hello_world():
    print(db.engine)
    data = Ranking.get_top_gainers(
        engine=db.engine, count_result=app.config.get("RESULT_COUNT"), days=5
    )
    return str(data)


@app.route("/{}".format(TOKEN), methods=["POST"])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode("utf-8").decode()
    # for debugging purposes only
    print("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Welcome to coolAvatar bot, the bot is using the service from http://avatars.adorable.io/ to generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with an avatar for your name.
       """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text == "5 дней":
        data = Ranking.get_top_gainers(
            engine=db.engine, count_result=app.config.get("RESULT_COUNT"), days=5
        )
        print(data)
        bot.sendMessage(chat_id=chat_id, text=data, reply_to_message_id=msg_id)

    elif text == "count":
        data = db.session.query(RankHistorical).all()
        bot.sendMessage(
            chat_id=chat_id, text=str(len(data)), reply_to_message_id=msg_id
        )
    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)
            # create the api link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # reply with a photo to the name the user sent,
            # note that you can send photos by url and telegram will fetch it for you
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        except Exception:
            # if things went wrong
            bot.sendMessage(
                chat_id=chat_id,
                text="There was a problem in the name you used, please enter different name",
                reply_to_message_id=msg_id,
            )

    return "ok"


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
