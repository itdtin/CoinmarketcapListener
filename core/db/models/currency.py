from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table

from .database import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)
    ticker = Column(String)
    last_update = Column(DateTime, default=datetime.utcnow())
    is_active = Column(Integer)
    cmc_current_rank = Column(Integer, nullable=True)
    platform = Column(String, ForeignKey("platforms.id"), nullable=True)

    def __init__(
        self,
        id: int,
        slug: str,
        ticker: str,
        last_update: datetime,
        is_active: int,
        cmc_current_rank: int = None,
        platform: str = None,
    ):
        self.id = id
        self.slug = slug
        self.ticker = ticker
        self.last_update = last_update
        self.is_active = is_active
        self.cmc_current_rank = cmc_current_rank
        self.platform = platform

    def __repr__(self):
        info: str = f"Currency: {self.ticker}, id:{self.id}, slug: {self.slug}, " f"active:{True if self.is_active == 1 else False}, rank:{self.cmc_current_rank}"
        return info
