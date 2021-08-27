from datetime import datetime

from sqlalchemy.orm import relationship

from app import db
from db.basicmodels import ComparableEntity


class Currency(ComparableEntity, db.Model):
    __tablename__ = "currencies"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    slug = db.Column(db.String)
    ticker = db.Column(db.String)
    cmc_current_rank = db.Column(db.Integer, nullable=True)


class RankHistorical(ComparableEntity, db.Model):
    __tablename__ = "rank_historical"
    id = db.Column(db.Integer, primary_key=True)
    cmc_id = db.Column(db.Integer, db.ForeignKey("currencies.id"))
    last_update = db.Column(db.Date, default=datetime.utcnow().date())
    rank = db.Column(db.Integer, nullable=True)
