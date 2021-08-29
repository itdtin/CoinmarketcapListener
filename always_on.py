from ranking import Ranking

CMC_API_TOKEN = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/"

r = Ranking(CMC_BASE_URL, CMC_API_TOKEN)
r.fill_cmc_data()
