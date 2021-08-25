from datetime import datetime

from sqlalchemy.exc import IntegrityError

from core.logger.logger import logger
from core.db.models.database import create_db, Session
from core.db.models.currency import Currency
from core.db.models.platform import Platform
from coinmarketcap.cmc_service import CMCService


def create_database(load_fake_data: bool = True):
    create_db()
    if load_fake_data:
        _load_cmc_data(Session())


def _load_cmc_data(session: Session):
    cmc = CMCService()
    current_cmc_data = cmc.get_id_map()
    for curr in current_cmc_data.get("data"):
        platform_slug = None
        if curr.get("platform"):

            platform_data = curr["platform"]
            platform_slug = platform_data["slug"]
            platform = Platform(
                slug=platform_slug,
                name=platform_data["name"],
                ticker=platform_data["symbol"],
                cmc_id=platform_data["id"],
            )
            existing = session.query(Platform).filter_by(slug=platform.slug).first()
            if not existing:  # Check to existing platform in current session
                session.add(platform)
            else:
                logger.debug(f"Tried to insert existing {platform}")
        currency = Currency(
            slug=curr["slug"],
            ticker=curr["symbol"],
            last_update=datetime.utcnow(),
            is_active=curr["is_active"],
            cmc_current_rank=curr.get("rank"),
            platform=platform_slug,
        )
        existing = session.query(Currency).filter_by(slug=currency.slug).first()
        if not existing:  # Check to existing currency in current session
            session.add(currency)
        else:
            logger.debug(f"Tried to insert existing {currency}")
    session.commit()
    session.close()
