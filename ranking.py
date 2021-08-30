from datetime import datetime, timedelta
import re
from dateutil.relativedelta import relativedelta

from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2

from core.utils.data_format import DateFormat, check_period_format


class Ranking:
    @staticmethod
    def define_range(**kwargs):
        end_date = datetime.utcnow() + timedelta(days=1)
        start_date = None
        if kwargs.get("days"):
            start_date = end_date - timedelta(days=kwargs.get("days"))
        if kwargs.get("weeks"):
            start_date = end_date - timedelta(weeks=kwargs.get("weeks"))
        if kwargs.get("months"):
            start_date = end_date - relativedelta(months=kwargs.get("months"))
        if kwargs.get("period"):
            start_date, end_date = check_period_format(kwargs.get("period"))

        assert start_date is not None and isinstance(
            start_date, datetime
        ), f"You should chose date from which will generated report"
        end_date_str = end_date.strftime(DateFormat.date_format.value)
        start_date_str = start_date.strftime(DateFormat.date_format.value)
        return start_date_str, end_date_str

    @classmethod
    def get_top_gainers(cls, engine, count_result: int, **kwargs):
        """Get top gainers
        :param engine:
        :param count_result: count of result
        :param kwargs - days=<int>, weeks=<int>, months=<int>
        """
        start_date_str, end_date_str = cls.define_range(**kwargs)

        sqlite_query = (
            f"select cmc_id, current_value, gain, max(created_date), c2.ticker, c2.slug "
            f"from (select cmc_id, last_update as created_date, rank as current_value, "
            f"(last_value(rank) over(partition by cmc_id order by last_update) - "
            f"first_value(rank) over(partition by cmc_id order by last_update)) as gain "
            f"from rank_historical rh where last_update between '{start_date_str}' and '{end_date_str}') as c1 "
            f"left join currencies c2 on c1.cmc_id=c2.id where gain > 0 group by cmc_id order by gain desc limit {count_result}"
        )

        postgres_query = (
            f"select cmc_id, c.ticker, a.first_value, a.last_value, gain "
            f"from (select rh.cmc_id as cmc_id, rh.last_update as update_date,"
            f"(first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) - "
            f"last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update)) as gain,"
            f"first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) first_value,"
            f"last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) last_value,"
            f"row_number() over(partition by rh.cmc_id order by rh.last_update desc) seq "
            f"from rank_historical rh where rh.last_update between '{start_date_str}' and '{end_date_str}') a "
            f"left join currencies c on a.cmc_id=c.id where seq = 1 and gain > 0 order by gain desc limit {count_result}"
        )
        query = None
        if isinstance(engine.dialect, SQLiteDialect_pysqlite):
            query = sqlite_query
        elif isinstance(engine.dialect, PGDialect_psycopg2):
            query = postgres_query
        assert query
        d = engine.execute(query).all()
        allowed_fiellds = ["cmc_id", "last_value", "first_value"]
        result = [
            [v for k, v in record.items() if k not in allowed_fiellds] for record in d
        ]
        return result
