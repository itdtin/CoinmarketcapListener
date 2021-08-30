from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2


class Ranking:
    @staticmethod
    def get_top_gainers(engine, count_result: int, **kwargs):
        """Get top gainers
        :param engine:
        :param count_result: count of result
        :param kwargs - days=<int>, weeks=<int>, months=<int>
        """
        global target_date_str
        date_format = "%Y-%m-%d"

        current_date = datetime.utcnow() + timedelta(days=1)
        curr_date_str = current_date.strftime(date_format)
        target_date = None
        if kwargs.get("days"):
            target_date = current_date - timedelta(days=kwargs.get("days"))
        if kwargs.get("months"):
            target_date = current_date - relativedelta(months=kwargs.get("days"))
        assert target_date is not None and isinstance(
            target_date, datetime
        ), f"You should chose date from which will generated report"
        target_date_str = target_date.strftime(date_format)

        sqlite_query = (
            f"select cmc_id, current_value, gain, max(created_date), c2.ticker, c2.slug "
            f"from (select cmc_id, last_update as created_date, rank as current_value, "
            f"(last_value(rank) over(partition by cmc_id order by last_update) - "
            f"first_value(rank) over(partition by cmc_id order by last_update)) as gain "
            f"from rank_historical rh where last_update between '{target_date_str}' and '{curr_date_str}') as c1 "
            f"left join currencies c2 on c1.cmc_id=c2.id where gain != 0 group by cmc_id order by gain desc limit {count_result}"
        )

        postgres_query = (
            f"select cmc_id, c.ticker, update_date, a.first_value, a.last_value, gain "
            f"from (select rh.cmc_id as cmc_id, rh.last_update as update_date,"
            f"(first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) - "
            f"last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update)) as gain,"
            f"first_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) first_value,"
            f"last_value(rh.cmc_rank) over(partition by rh.cmc_id order by rh.last_update) last_value,"
            f"row_number() over(partition by rh.cmc_id order by rh.last_update desc) seq "
            f"from rank_historical rh  where rh.last_update between '{target_date_str}' and '{curr_date_str}') a "
            f"left join currencies c on a.cmc_id=c.id where seq = 1 and gain != 0 order by gain desc limit {count_result}"
        )
        query = None
        if isinstance(engine.dialect, SQLiteDialect_pysqlite):
            query = sqlite_query
        elif isinstance(engine.dialect, PGDialect_psycopg2):
            query = postgres_query
        assert query
        print(query)
        d = engine.execute(query).all()
        result = [{k: v for k, v in record.items()} for record in d]
        return result
