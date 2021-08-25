from coinmarketcap.cmc_client import CMCClient


class CMCService(CMCClient):
    api_token = "2229a7b0-ebf1-403f-8470-7c32d0feefa2"
    base_url = "https://pro-api.coinmarketcap.com/"

    def __init__(self):
        super(CMCService, self).__init__(self.base_url, self.api_token)




if __name__ == '__main__':
    c = CMCService()
    d = c.get_id_map()
    print(d)