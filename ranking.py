from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
                logger.debug(f"Updated Currency: {currency_data['slug']}")

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

    @staticmethod
    def get_top_gainers(**kwargs):
        """Get top gainers
        :param kwargs - days=<int>, weeks=<int>, months=<int>
        """
        global target_date_str
        from db.cmc_entities_models import RankHistorical

        current_date = datetime.utcnow() + timedelta(days=1)
        curr_date_str = current_date.strftime("%Y-%m-%d")
        if kwargs.get("days"):
            target_date = current_date - timedelta(days=kwargs.get("days"))
            target_date_str = target_date.strftime("%Y-%m-%d")
        if kwargs.get("months"):
            target_date = current_date - relativedelta(months=kwargs.get("days"))
            target_date_str = target_date.strftime("%Y-%m-%d")

        query = (
            f"select cmc_id, current_value, gain, max(created_date), c2.ticker, c2.slug "
            f"from (select cmc_id, last_update as created_date, rank as current_value, "
            f"(last_value(rank) over(partition by cmc_id order by last_update) - "
            f"first_value(rank) over(partition by cmc_id order by last_update)) as gain "
            f"from rank_historical rh where last_update between '{target_date_str}' and '{curr_date_str}') "
            f"left join currencies c2 on cmc_id=c2.id where gain != 0 group by cmc_id order by gain desc"
        )
        import app

        d = app.db.engine.execute(query).all()
        result = [{k: v for k, v in record.items()} for record in d]
        return result[: app.config.RESULT_COUNT]
