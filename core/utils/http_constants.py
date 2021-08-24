from enum import Enum


class HttpHeadersKeys(Enum):
    content_type = "Content-type"
    accept = "Accept"
    user_agent = "User-Agent"
    cmc_api_token = "X-CMC_PRO_API_KEY"


class HttpHeaderValues(Enum):
    app_json = "application/json"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15"
