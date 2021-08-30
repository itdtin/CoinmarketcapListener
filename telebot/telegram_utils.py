import prettytable as pt
from enum import Enum
from datetime import datetime
import re

from core.logger.logger import logger


def create_table_to_send(data):
    table = pt.PrettyTable(["Ticker", "Gain"])
    table.align["Ticker"] = "l"
    table.align["Gain"] = "r"

    for ticker, gain in data:
        table.add_row([ticker, gain])

    return table


def define_query_params(text: str):
    assert len(text.lower().split(" ")) == 2
    count, period = text.lower().split(" ")

    if count.startwith("period"):
        period = "period"
        count = text.lower().split("period")[1].strip()
        return dict({period: count})
    elif period.startwith("month"):
        period = "months"
    elif period.startwith("week"):
        period = "weeks"
    elif period.startwith("day"):
        period = "days"
    else:
        logger.error(f"Undefined period: {period}")
    try:
        count = int(count)
        return dict({period: count})
    except:
        logger.error(f"Incorrect count: {count} for {period}")
