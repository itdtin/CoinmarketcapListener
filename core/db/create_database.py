from datetime import datetime

from sqlalchemy.exc import IntegrityError

from core.logger.logger import logger
from core.db.models.database import create_db, Session
from core.db.models.currency import Currency
from core.db.models.platform import Platform
from coinmarketcap.cmc_client import Coinmarketcap


def create_database(load_fake_data: bool = True):
    create_db()
    if load_fake_data:
        _load_cmc_data()


def _load_cmc_data():
    cmc = Coinmarketcap()
    session = Session()
    current_cmc_data = cmc.get_id_map()
    logger.error(len(current_cmc_data))
    for curr in current_cmc_data:
        platform_id = None
        if curr.get("platform"):
            platform_data = curr["platform"]
            platform_id = platform_data["id"]
            existing = session.query(Platform).filter_by(id=platform_id).first()
            if not existing:  # Check to existing platform in current session
                platform = create_platform(platform_data)
                session.add(platform)
            else:
                logger.debug(
                    f"Tried to insert existing platform with id: {platform_id}"
                )
        existing = session.query(Currency).filter_by(id=curr["id"]).first()
        if not existing:  # Check to existing currency in current session
            currency = create_currency(curr, platform_id)
            session.add(currency)
        else:
            logger.debug(f"Tried to insert existing currency with slug: {curr['slug']}")
    session.commit()
    session.close()


def create_platform(platform_data: dict) -> Platform:
    platform = Platform(
        id=platform_data["id"],
        slug=platform_data["slug"],
        name=platform_data["name"],
        ticker=platform_data["symbol"],
    )
    return platform


def create_currency(currency_data: dict, platform_id: int = None) -> Currency:
    currency = Currency(
        id=currency_data["id"],
        slug=currency_data["slug"],
        ticker=currency_data["symbol"],
        last_update=datetime.utcnow(),
        is_active=currency_data["is_active"],
        cmc_current_rank=currency_data.get("rank"),
        platform=platform_id,
    )
    return currency
