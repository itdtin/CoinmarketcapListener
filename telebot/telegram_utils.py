import prettytable as pt
from enum import Enum
from datetime import datetime
import re

from core.logger.logger import logger


def create_table_to_send(data):
    table = pt.PrettyTable(["Ticker", "Slug", "Gain"])
    table.align["Ticker"] = "l"
    table.align["Slug"] = "l"
    table.align["Gain"] = "r"

    for ticker, slug, gain in data:
        table.add_row([ticker, slug, gain])

    return table


def define_query_params(text: str) -> dict:
    assert len(text.lower().split(" ")) == 2
    count, period = text.lower().split(" ")
    if count.startswith("period"):
        period = "period"
        count = text.lower().split("period")[1].strip()
        return dict({period: count})
    elif period.startswith("month"):
        period = "months"
    elif period.startswith("week"):
        period = "weeks"
    elif period.startswith("day"):
        period = "days"
    else:
        logger.error(f"Undefined period: {period}")
    try:
        count = int(count)
        return dict({period: count})
    except:
        return dict()
        logger.error(f"Incorrect count: {count} for {period}")
