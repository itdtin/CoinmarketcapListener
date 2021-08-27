from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from core.logger.logger import logger

# from ranking.ranking import Ranking

#
# def sensor():
#     """ Function for test purposes. """
#
#     rank_listener.fill_cmc_data(db.session)
#
#
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(sensor, "interval", seconds=30)
# sched.start()

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
db = SQLAlchemy(app)
# with app.app_context():
#     from db.cmc_entities_models import Currency, RankHistorical
#     from db.fill_cmc_data import fill_cmc_data as fill
#
#     db.create_all()
#     rank_listener = Ranking(
#         app.config.get("CMC_BASE_URL"), app.config.get("CMC_API_TOKEN")
#     )
#     sensor()
# migrate = Migrate(app, db)


@app.route("/")
def hello_world():
    from db.cmc_entities_models import Currency

    data = db.session.query(Currency).all()
    return str(data)


if __name__ == "__main__":
    app.run()
