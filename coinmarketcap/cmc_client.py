from http import HTTPStatus

from core.clients.api.baseclient import BaseAPIClient
from coinmarketcap.endpoints import CMCEndpoints
from core.utils.http_constants import HttpHeaderValues, HttpHeadersKeys
from core.logger.logger import logger


class Coinmarketcap(BaseAPIClient):
    """Class for working with Sapio Exemplar"""

    def __init__(self, base_url: str, api_token: str):
        super(Coinmarketcap, self).__init__(base_url, api_token)
        self.headers = {
            HttpHeadersKeys.cmc_api_token.value: api_token,
            HttpHeadersKeys.accept.value: HttpHeaderValues.app_json.value,
        }
        self.set_headers(self.headers)
        self.endpoints = CMCEndpoints
        self.ssl_verification_check()

    def get_id_map(self):
        """Get full ID Map"""
        path = self.endpoints.map.value
        result = self.get(path)
        if result.status_code == HTTPStatus.OK:
            return result.json()["data"]
        return result

    def get_info(self):
        path = self.endpoints.info.value
        result = self.get(path)
        if result.status_code == HTTPStatus.OK:
            return result.json()
        return result
