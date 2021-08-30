import prettytable as pt
from telegram import ParseMode
from telegram.ext import CallbackContext, Updater


def create_table_to_send():
    table = pt.PrettyTable(["Ticker", "Gain_Range", "Gain"])
    table.align["Ticker"] = "l"
    table.align["Gain_Range"] = "r"
    table.align["Gain"] = "r"

    data = [
        ("ABC", 20.85, 1.626),
        ("DEF", 78.95, 0.099),
        ("GHI", 23.45, 0.192),
        ("JKL", 98.85, 0.292),
    ]
    for symbol, price, change in data:
        table.add_row([symbol, f"{price:.2f}", f"{change:.3f}"])

    return table
