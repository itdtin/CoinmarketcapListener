from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Platform(Base):
    __tablename__ = "platform"

    slug = Column(String, primary_key=True)
    name = Column(String)
    ticker = Column(String)
    cmc_id = Column(Integer)
    tokens_buillded = relationship("Currency")

    def __repr__(self):
        return (
            f"Platform {self.name} with ticker:{self.ticker}, sllug:{self.slug}, cmc_id:{self.cmc_id}, "
            f"tokens builded on this platform: {self.tokens_buillded}"
        )
