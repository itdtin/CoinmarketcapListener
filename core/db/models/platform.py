from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Platform(Base):
    __tablename__ = "platforms"

    slug = Column(String, unique=True)
    name = Column(String)
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
