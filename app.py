from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy

from core.logger.logger import logger


def sensor():
    """ Function for test purposes. """
    from db.fill_cmc_data import fill_cmc_data as fill

    fill(db.session)


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, "interval", minutes=60)
sched.start()

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)
with app.app_context():
    from db.cmc_entities_models import Platform, Currency
    from db.fill_cmc_data import fill_cmc_data as fill

    db.create_all()
    fill(db.session)


@app.route("/")
def hello_world():
    data = db.session.query(Platform).all()
    return str(data)


if __name__ == "__main__":
    app.run()
