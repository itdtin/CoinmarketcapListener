import os

from sqlalchemy import and_

from models.database import DATABASE_NAME, Session
import create_database as db_creator
from models.currency import Currency
from models.platform import Platform
from core.db.models.database import Session


if __name__ == "__main__":
    # db_creator._load_cmc_data(Session())
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        db_creator.create_database()
    else:
        db_creator._load_cmc_data()
