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
from ranking import Ranking
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
migrate = Migrate(app, db)


sched = BackgroundScheduler(daemon=True, timezone="UTC")
# sched.add_job(sensor, "interval", seconds=10)
sched.add_job(rank_listener.fill_cmc_data, trigger="cron", hour="0")
sched.start()


@app.route("/")
def hello_world():
    data = Ranking.get_top_gainers(
        engine=db.engine, count_result=app.config.get("RESULT_COUNT"), days=5
    )
    return str(data)


@app.route("/{}".format(TOKEN), methods=["POST"])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.effective_message.chat.id
    msg_id = update.effective_message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode("utf-8").decode()
    # for debugging purposes only
    print("got text message :", text)
    if text == "/start":
        bot_welcome = """Welcome to ranking bot.\nAllowed commands:\n
        1. /update_data - upload current Coinmarketcap data.\n
        2. /info - Show allowed periods for query top gainers"""
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text == "/count":
        data = db.session.query(RankHistorical).all()
        bot.sendMessage(
            chat_id=chat_id, text=str(len(data)), reply_to_message_id=msg_id
        )

    elif text == "/update_data":
        rank_listener.fill_cmc_data()
        bot.sendMessage(
            chat_id=chat_id,
            text="Coinmarketcap data is up to date",
            reply_to_message_id=msg_id,
        )

    elif text == "/info":
        text_msg = (
            f"Possible the following commands to get top gainers via date period:\n\n"
            f"1. <b>Day:</b> 'count day' or 'count days' - show top gainers for past count of days.\n\n"
            f"2. <b>Week:</b> 'count week' or 'count weeks' - show top gainers for past count of weeks.\n\n"
            f"3. <b>Months:</b> 'count month' or 'count months' - show top gainers for past count of months.\n\n"
            f"4. <b>Period:</b> 'period date_start-date_end' - show top gainers for passed period.\n"
            f"<b>Note:</b> <i>Be aware the format of date_start and date_end is yyyy.mm.dd, "
            f"so full query will be like: period 2021.08.01-2021.08.31</i>"
        )
        bot.sendMessage(
            chat_id=chat_id,
            text=text_msg,
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
        )

    elif len(text.strip().split(" ")) == 2:
        range_param = define_query_params(text)
        if isinstance(range_param, dict) and len(range_param.items()) > 0:
            data = Ranking.get_top_gainers(
                engine=db.engine,
                count_result=app.config.get("RESULT_COUNT"),
                **range_param,
            )
            logger.error(data)
            if data:
                data = create_table_to_send(data)
            else:
                data = "No data exist for gainers in chosen period"

            bot.sendMessage(
                chat_id=chat_id,
                text=f"```{data}```",
                reply_to_message_id=msg_id,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            bot.sendMessage(
                chat_id=chat_id,
                text=f"<s>{text}</s>\nIncorrect query!!!",
                parse_mode=ParseMode.HTML,
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
