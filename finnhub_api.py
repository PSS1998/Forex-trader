import requests

from exceptions import FinnhubAPIException
from exceptions import FinnhubRequestException



class Client:
    API_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key, requests_params=None):
        self.api_key = api_key
        self.session = self._init__session()
        self._requests_params = requests_params

    def _init__session(self):
        session = requests.session()
        session.headers.update({'Accept': 'application/json',
                                'User-Agent': 'finnhub/python'})
        return session

    def _request(self, method, uri, **kwargs):
        kwargs['timeout'] = 10
        data = kwargs.get('data', None)

        if data and isinstance(data, dict):
            kwargs['data'] = data
        else:
            kwargs['data'] = {}

        kwargs['data']['token'] = self.api_key
        kwargs['params'] = kwargs['data']

        del(kwargs['data'])
        response = getattr(self.session, method)(uri, **kwargs)

        return self._handle_response(response)

    def _create_api_uri(self, path):
        return "{}/{}".format(self.API_URL, path)

    def _request_api(self, method, path, **kwargs):
        uri = self._create_api_uri(path)
        return self._request(method, uri, **kwargs)

    def _handle_response(self, response):
        if not str(response.status_code).startswith('2'):
            raise FinnhubAPIException(response)
        try:
            return response.json()
        except ValueError:
            raise FinnhubRequestException("Invalid Response: {}".format(response.text))

    def _merge_two_dicts(self, a, b):
        result = a.copy()
        result.update(b)
        return result

    def _str_to_bool(self, **kwargs):
        for i in kwargs:
            if (kwargs[i] == True): kwargs[i] = "true"
            elif (kwargs[i] == False): kwargs[i] = "false"
        return kwargs

    def _get(self, path, **kwargs):
        params = self._str_to_bool(**kwargs)
        return self._request_api('get', path, **params)

    def forex_exchanges(self):
        return self._get("/forex/exchange")

    def forex_rates(self, **params):
        return self._get("/forex/rates", data=params)

    def forex_symbols(self, exchange):
        return self._get("/forex/symbol", data={
            "exchange": exchange
        })

    def forex_candles(self, symbol, resolution, _from, to, format=None):
        return self._get("/forex/candle", data={
            "symbol": symbol,
            "resolution": resolution,
            "from": _from,
            "to": to,
            "format": format
        })


# finnhub_client = Client(api_key="bsgta37rh5rdc8pmr8dg")

# Forex exchanges
# print(finnhub_client.forex_exchanges())

# Forex all pairs
# print(finnhub_client.forex_rates(base='USD'))

# Forex symbols
# print(finnhub_client.forex_symbols('fxpro'))

# Forex candles
# ticker = finnhub_client.forex_candles('FXPRO:4', '5', 1593604800, 1596110400)
# ticker = data_handler.ohlcv_load_from_dict(ticker)
# print(ticker)