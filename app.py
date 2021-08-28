import atexit

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from ranking import Ranking


def sensor():
    """ Function for test purposes. """

    rank_listener.fill_cmc_data(db.session)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, "interval", days=1)
sched.start()


app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
db = SQLAlchemy(app)

with app.app_context():
    from db.cmc_entities_models import Currency, RankHistorical

    db.create_all()
    rank_listener = Ranking(
        app.config.get("CMC_BASE_URL"), app.config.get("CMC_API_TOKEN")
    )
    # rank_listener.fill_cmc_data(db.session)
migrate = Migrate(app, db)


@app.route("/")
def hello_world():

    data = rank_listener.get_top_gainers(days=1)
    return str(data)


# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())


if __name__ == "__main__":
    app.run()
