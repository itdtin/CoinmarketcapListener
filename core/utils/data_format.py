from enum import Enum
import re
from datetime import datetime
from core.logger.logger import logger


class DateFormat(Enum):

    date_format = "%Y-%m-%d"
    date_re = r"([0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]))"
    period_re = rf"{date_re}--{date_re}"


def check_period_format(period_str: str, only_check: bool = False):
    match = re.match(DateFormat.period_re.value, period_str)
    if match:
        if only_check:
            return True
        else:
            period = match.group().split("--")
            start_date = datetime.strptime(period[0], DateFormat.date_format.value)
            end_date = datetime.strptime(period[1], DateFormat.date_format.value)
            return start_date, end_date
    return None
