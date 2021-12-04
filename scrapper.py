import config
import http_client as client
from lxml import html
import re
import json

element = {
    'price': 0.0,
    'quantity': 0,
    'shippingMethods': []
}


def get_markets(option):
    if option == 1:
        return get_markets_casto()
    if option == 2:
        return get_markets_leroy()
    if option == 3:
        return get_markets_obi()
    return None


def get_product_details(product_id, market_id, option):
    if option == 1:
        return get_product_details_casto(product_id, market_id)
    if option == 2:
        return get_product_details_leroy(product_id, market_id)
    if option == 3:
        return get_product_details_obi(product_id, market_id)
    return None


def get_markets_casto():
    response = client.send_get(config.CASTO_MARKETS_URL)
    markets = response.json() if response.status_code == 200 else {}
    return {m['selected_shop_store_view']: m['name'] for m in markets}


def get_product_details_casto(product_id, market_id):
    response = client.send_get(config.CASTO_PRODUCT_URL.format(market_id, product_id))
    data = response.json()
    element['price'] = float(data['products'][product_id]['price'])
    element['qty'] = int(data['products'][product_id]['qty'])
    try:
        element['shippingMethods'] = [e[0] for e in data['products'][product_id]['shippingMethods'].items() if
                                      e[1] is True]
    except (IndexError, KeyError):
        element['shippingMethods'] = 'N/A'

    return element


def get_markets_leroy():
    response = client.send_get(config.LEROY_MARKETS_URL)
    parser = html.HTMLParser(encoding="utf-8")
    dom = html.document_fromstring(response.content, parser=parser)
    markets = dom.xpath('//option[@value]')
    return {m.attrib['value']: m.text for m in markets}


def get_product_details_leroy(product_id, market_id):
    response = client.send_get(config.LEROY_PRODUCT_URL.format(product_id, market_id))
    data = response.json()
    try:
        element['price'] = float(data[0]['storePriceDto']['priceSetDto']['bigPriceDecimal'])
    except (IndexError, KeyError):
        element['price'] = 99999.99
    try:
        element['qty'] = int(data[0]['storeStockDto']['quantity'])
    except (IndexError, KeyError):
        element['qty'] = -1
    element['shippingMethods'] = ['N/A']

    return element


def get_markets_obi():
    response = client.send_get(config.OBI_MARKETS_URL)
    parser = html.HTMLParser(encoding="utf-8")
    dom = html.document_fromstring(response.content, parser=parser)
    markets = json.loads(dom.xpath('//script[@type="application/ld+json"]/text()')[0])
    return {m['branchCode']: m['name'] for m in markets['hasPOS']}


def get_product_details_obi(product_id, market_id):
    header = {'User-Agent': 'Chrome/86.0.4240.198'}
    response = client.send_get_with_session(config.OBI_PRODUCT_URL.format(market_id.zfill(3), product_id), header)
    parser = html.HTMLParser(encoding="utf-8")
    dom = html.document_fromstring(response.content, parser=parser)
    try:
        element['price'] = float(str(dom.xpath('//strong[@data-ui-name="ads.price.strong"]')[0].text).replace(',', '.'))
    except (IndexError, KeyError):
        element['price'] = 99999.99
    try:
        element['qty'] = \
            re.findall("[0-9]+", str(dom.xpath('//p[@data-ui-name="instore.adp.availability_message"]')[0].text))[0]
    except (IndexError, KeyError):
        element['qty'] = -1
    element['shippingMethods'] = ['N/A']

    return element
