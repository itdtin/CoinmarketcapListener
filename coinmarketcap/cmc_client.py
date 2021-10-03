from http import HTTPStatus
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

from core.clients.api.baseclient import BaseAPIClient
from coinmarketcap.endpoints import CMCEndpoints
from core.utils.http_constants import HttpHeaderValues, HttpHeadersKeys
from core.logger.logger import logger
from config import Config


class Coinmarketcap(BaseAPIClient):
    """Class for working with Sapio Exemplar"""

    def __init__(self, base_url: str, api_token: str, db_engine):
        super(Coinmarketcap, self).__init__(base_url, api_token)
        self.headers = {
            HttpHeadersKeys.cmc_api_token.value: api_token,
            HttpHeadersKeys.accept.value: HttpHeaderValues.app_json.value,
        }
        self.set_headers(self.headers)
        self.endpoints = CMCEndpoints
        self.ssl_verification_check()
        self.db_engine = db_engine
        self.Session = sessionmaker(db_engine)

    @classmethod
    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def get_id_map(self):
        """Get full ID Map"""
        path = self.endpoints.map.value
        result = self.get(path)
        if result.status_code == HTTPStatus.OK:
            return result.json()["data"]
        return result

    def get_info(self):
        path = self.endpoints.info.value
        result = self.get(path)
        if result.status_code == HTTPStatus.OK:
            return result.json()
        return result

    def rotate_data_in_db(self):
        """Check rotate period and delete oldest records"""
        try:
            rotate_period_proper_start_date = (
                datetime.now() - timedelta(days=Config.ROTATE_PERIOD)
            ).strftime("%Y-%m-%d") + " 00:00:00"
            query = f"delete from rank_historical where last_update < '{rotate_period_proper_start_date}'"
            self.db_engine.execute(query)
        except Exception as e:
            logger.error(e)

    def fill_cmc_data(self):
        self.rotate_data_in_db()
        current_cmc_data = self.get_id_map()
        with self.Session() as session:
            for curr in current_cmc_data[:100]:  # Todo delete slice into production
                self.fill_and_update_currency_and_related_tables(curr, session)
            session.commit()
        logger.error(f"Updated CoinMarketCap data")

    def fill_and_update_currency_and_related_tables(self, currency_data: dict, session):
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
                cmc_rank=currency_data.get("rank"),
            )
            return currency


if __name__ == "__main__":
    c = Coinmarketcap()
