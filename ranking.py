from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


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

        query = (
            f"select cmc_id, current_value, gain, max(created_date), c2.ticker, c2.slug "
            f"from (select cmc_id, last_update as created_date, rank as current_value, "
            f"(last_value(rank) over(partition by cmc_id order by last_update) - "
            f"first_value(rank) over(partition by cmc_id order by last_update)) as gain "
            f"from rank_historical rh where last_update between '{target_date_str}' and '{curr_date_str}') as c1 "
            f"left join currencies c2 on c1.cmc_id=c2.id where gain != 0 group by cmc_id order by gain desc"
        )
        d = engine.execute(query).all()
        result = [{k: v for k, v in record.items()} for record in d[:count_result]]
        return result
