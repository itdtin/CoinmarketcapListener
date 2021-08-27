from datetime import datetime, timedelta
from typing import Union, List

import pandas as pd

from coinmarketcap.cmc_client import Coinmarketcap
from core.logger.logger import logger


class Ranking:
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
            to_be_updated.last_update = datetime.utcnow()
            to_be_updated.rank = currency_data.get("rank")
            return to_be_updated
        else:
            currency = RankHistorical(
                cmc_id=currency_data["id"],
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
        :param kwargs - days=<int>, weeks=<int>, months=<int>
        """
        from db.cmc_entities_models import RankHistorical

        current_date = datetime.utcnow().date()
        curr_date_str = current_date.strftime("%Y-%m-%d")
        if kwargs.get("days"):
            target_date = current_date - timedelta(days=kwargs.get("days"))
            target_date_str = target_date.strftime("%Y-%m-%d")
        d = (
            session.query(RankHistorical)
            .filter(RankHistorical.last_update.between(target_date_str, curr_date_str))
            .all()
        )

        from core.utils.new_encoder import AlchemyEncoder
        import json

        # todo handle request
        f"select cmc_id, min_max_date_rank_diff from(" f"select cmc_id, last_update as created_date, rank as value, " f"(first_value(rank) over(partition by cmc_id order by last_update asc) - " f"first_value(rank) over(partition by cmc_id order by last_update desc)) as min_max_date_rank_diff," f"row_number() over(PARTITION by cmc_id order by last_update) num," f"rank() over(partition by cmc_id order by rank) rank_rank," f"DENSE_RANK () over(partition by cmc_id order by rank) dense_rank_rank " f"from rank_historical rh " f"where last_update between '2021-08-24' and '2021-08-27') group by cmc_id"


if __name__ == "__main__":
    from app import db

    CMC_API_TOKEN = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
    CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"
    r = Ranking(CMC_BASE_URL, CMC_API_TOKEN)
    d = r.get_top_gainers(db.session, days=1)
