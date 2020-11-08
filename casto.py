import config
import http_client as client


def get_markets():
    response = client.send_get(config.MARKETS_URL)
    markets = response.json() if response.status_code == 200 else {}
    return {m['selected_shop_store_view']: m['name'] for m in markets}


def get_product_details(product_id, market_id):
    response = client.send_get(config.PRODUCT_URL.format(market_id, product_id))
    return response.json()
