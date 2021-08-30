import prettytable as pt
from telegram import ParseMode
from telegram.ext import CallbackContext, Updater


def create_table_to_send(data):
    table = pt.PrettyTable(["Ticker", "Gain"])
    table.align["Ticker"] = "l"
    table.align["Gain"] = "r"

    for ticker, gain in data:
        table.add_row([ticker, gain])

    return table
