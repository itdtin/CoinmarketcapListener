from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from .database import Base


class Currency(Base):
    __tablename__ = "currency"

    slug = Column(String, primary_key=True)
    ticker = Column(String)
    last_update = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer)
    cmc_current_rank = Column(Integer, nullable=True)
    platform = Column(String, ForeignKey("platforms.slug"), nullable=True)

    def __init__(
        self,
        slug: str,
        ticker: str,
        last_update: datetime,
        is_active: int,
        cmc_current_rank: int = None,
        platform: str = None,
    ):
        self.slug = slug
        self.ticker = ticker
        self.last_update = last_update
        self.is_active = is_active
        self.cmc_current_rank = cmc_current_rank
        self.platform = platform

    def __repr__(self):
        info: str = f"Currency: {self.ticker}, slug: {self.slug}, active:{True if self.is_active == 1 else False}, rank:{self.cmc_current_rank}"
        return info
