from datetime import datetime
from typing import Union, List

from coinmarketcap.cmc_client import Coinmarketcap
from core.logger.logger import logger


class RankListener:
    def __init__(self, cmc_base_url: str, cmc_api_token: str):
        self.cmc = Coinmarketcap(cmc_base_url, cmc_api_token)

    def fill_cmc_data(self, session):
        current_cmc_data = self.cmc.get_id_map()
        for curr in current_cmc_data:
            self.fill_and_update_currency_and_related_tables(session, curr)
        session.commit()
        session.close()
        logger.error(f"Updated CoinMarketCap data")

    def fill_and_update_currency_and_related_tables(self, session, currency_data: dict):
        """Fill Currency record and related Platform record and fill rank_historical record"""
        from db.cmc_entities_models import Currency

        existing = session.query(Currency).filter_by(id=currency_data["id"]).first()
        currency = self.create_update_currency(currency_data)
        rank = self.create_update_rank_historical(currency_data)
        session.add(rank)
        if not existing:  # Check to existing currency in current session
            session.add(currency)
        else:
            to_update = Currency.query.filter_by(id=currency_data["id"]).first()
            if not currency == to_update:
                self.create_update_currency(currency_data, to_update)
                session.commit()
                logger.error(f"Updated Currency: {currency_data['slug']}")

    @staticmethod
    def create_update_currency(currency_data: dict, to_be_updated=None):
        from db.cmc_entities_models import Currency

        if to_be_updated:
            to_be_updated.id = currency_data["id"]
            to_be_updated.slug = currency_data["slug"]
            to_be_updated.ticker = currency_data["symbol"]
            to_be_updated.cmc_current_rank = currency_data.get("rank")
            return to_be_updated
        else:
            currency = Currency(
                id=currency_data["id"],
                slug=currency_data["slug"],
                ticker=currency_data["symbol"],
                cmc_current_rank=currency_data.get("rank"),
            )
            return currency

    @staticmethod
    def create_update_rank_historical(currency_data: dict, to_be_updated=None):
        from db.cmc_entities_models import RankHistorical

        if to_be_updated:
            to_be_updated.cmc_id = currency_data["id"]
            to_be_updated.slug = currency_data["slug"]
            to_be_updated.ticker = currency_data["symbol"]
            to_be_updated.last_update = datetime.utcnow()
            to_be_updated.rank = currency_data.get("rank")
            return to_be_updated
        else:
            currency = RankHistorical(
                cmc_id=currency_data["id"],
                slug=currency_data["slug"],
                ticker=currency_data["symbol"],
                last_update=datetime.utcnow(),
                rank=currency_data.get("rank"),
            )
            return currency

    def get_top_gainers(
        self, session, parameter: Union[str, List[str]] = "rank", **kwargs
    ):
        """Get top gainers
        :param session: session instance
        :param parameter: parameter via which will sort
        :param kwargs -
        """
