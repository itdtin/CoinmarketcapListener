import atexit

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from coinmarketcap.cmc_client import Coinmarketcap
from routes.telegram_routes import telegram_routes
from routes.ui_routes import ui_routes


app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
app.register_blueprint(telegram_routes)
app.register_blueprint(ui_routes)

global bot
global TOKEN


with app.app_context():
    from db.cmc_entities_models import Currency, RankHistorical

    db.create_all()
    rank_listener = Coinmarketcap(
        app.config.get("CMC_BASE_URL"), app.config.get("CMC_API_TOKEN"), db.engine
    )
    rank_listener.fill_cmc_data()
migrate = Migrate(app, db)


sched = BackgroundScheduler(daemon=True, timezone="UTC")
sched.add_job(
    rank_listener.fill_cmc_data, trigger="cron", hour="0"
)  # Run every day at 0:00:00
sched.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


if __name__ == "__main__":

    app.run(threaded=True)
