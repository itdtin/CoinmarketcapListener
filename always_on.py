from ranking import Ranking

from app import db

CMC_API_TOKEN = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

if __name__ == "__main__":
    r = Ranking(CMC_BASE_URL, CMC_API_TOKEN, db)
    r.fill_cmc_data()
