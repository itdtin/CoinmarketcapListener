import requests
from requests import Response
from urllib.parse import urljoin
import json
from urllib3.exceptions import InsecureRequestWarning

from core.utils.decorators import log_api
from core.logger.logger import logger
from core.utils.http_constants import HttpHeaderValues, HttpHeadersKeys


class BaseAPIClient:

    default_headers = {
        HttpHeadersKeys.content_type.value: HttpHeaderValues.app_json.value,
        HttpHeadersKeys.user_agent.value: HttpHeaderValues.user_agent.value,
    }

    def __init__(
        self,
        base_url,
        user: str = None,
        password: str = None,
        auth_token: str = None,
        api_token: str = None,
    ):
        self.user = user
        self.password = password
        self.auth_token = auth_token
        self._api_token = api_token
        self._api_base_url = base_url
        self._session = requests.Session()
        self._session.headers.update(self.default_headers)
        self._ssl_check = False

    def _call(self, method, path, params: dict = None, data=None, headers: dict = None):

        if str(method).upper() not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("invalid method <{0}>".format(method))
        url = urljoin(self._api_base_url, path)
        self.set_headers(headers)
        try:
            resp = self._session.request(
                method,
                url,
                params=params,
                data=json.dumps(data),
                verify=self._ssl_check,
            )
            return resp
        except ConnectionError:
            logger.warning("Connection error")

    def ssl_verification_check(self):
        if not self._ssl_check:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    def set_headers(self, headers):
        """Set headers to _session"""
        if headers is not None and isinstance(headers, dict):
            self._session.headers.update(headers)

    @log_api
    def post(
        self, path: str, params: dict = None, data=None, headers: dict = None
    ) -> Response:
        """Post request"""
        return self._call("POST", path, params=params, data=data, headers=headers)

    @log_api
    def get(
        self, path: str, params: dict = None, data=None, headers: dict = None
    ) -> Response:
        """Get request"""
        return self._call("GET", path, params=params, data=data, headers=headers)

    @log_api
    def put(
        self, path: str, params: dict = None, data=None, headers: dict = None
    ) -> Response:
        """Put request"""
        return self._call("PUT", path, params=params, data=data, headers=headers)

    @log_api
    def delete(
        self, path: str, params: dict = None, data=None, headers: dict = None
    ) -> Response:
        """Put request"""
        return self._call("DELETE", path, params=params, data=data, headers=headers)

    @log_api
    def update(
        self, path: str, params: dict = None, data=None, headers: dict = None
    ) -> Response:
        """Put request"""
        return self._call("PUT", path, params=params, data=data, headers=headers)
