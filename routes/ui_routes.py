from flask import Blueprint
import telegram
from sqlalchemy import create_engine


from config import Config
from core.logger.logger import logger
from ranking.ranking import Ranking


ui_routes = Blueprint("ui_routes", __name__)


@ui_routes.route("/")
def hello_world():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    data = Ranking.get_top_gainers(
        engine=engine, count_result=Config.RESULT_COUNT, days=5
    )
    return str(data)
