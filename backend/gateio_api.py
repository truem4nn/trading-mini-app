import requests
import hashlib
import hmac
import time
import urllib.parse
from config import GATEIO_API_KEY, GATEIO_API_SECRET, GATEIO_BASE_URL

def gen_sign(method, url, query_params=None, body=""):
    t = str(int(time.time()))
    if query_params:
        sorted_keys = sorted(query_params.keys())
        query_string = urllib.parse.urlencode([(k, query_params[k]) for k in sorted_keys])
    else:
        query_string = ""
    message = f"{method}\n{url}\n{query_string}\n{body}\n{t}"
    m = hashlib.sha512()
    m.update(message.encode())
    sign = hmac.new(GATEIO_API_SECRET.encode(), m.digest(), hashlib.sha512).hexdigest()
    headers = {
        "KEY": GATEIO_API_KEY,
        "Timestamp": t,
        "SIGN": sign,
        "Content-Type": "application/json"
    }
    return headers

def public_request(endpoint, params=None):
    url = f"{GATEIO_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, params=params)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def auth_request(method, endpoint, query_params=None, body=""):
    headers = gen_sign(method, endpoint, query_params, body)
    url = f"{GATEIO_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=query_params)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=body)
        else:
            return {"error": "Method tidak didukung"}
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def get_ticker(currency_pair):
    return public_request("/spot/tickers", {"currency_pair": currency_pair})

def get_order_book(currency_pair, limit=10):
    return public_request("/spot/order_book", {"currency_pair": currency_pair, "limit": limit})

def get_spot_accounts():
    return auth_request("GET", "/spot/accounts")