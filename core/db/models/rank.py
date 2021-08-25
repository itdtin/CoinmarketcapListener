from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Rank(Base):
    __tablename__ = "ranks"

    currency_id = Column(Integer, ForeignKey("currencies.id"))
    # a = Column(String)
    ticker = Column(String)
    id = Column(Integer, primary_key=True)
    tokens_builded_on = relationship("Currency")

    def __init__(self, slug: str, name: str, ticker: str, id: int):
        self.slug = slug
        self.name = name
        self.ticker = ticker
        self.id = id

    def __repr__(self):
        return f"Platform:{self.name}, ticker:{self.ticker}, slug:{self.slug}, cmc_id:{self.id}"
