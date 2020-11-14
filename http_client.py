import requests


def send_get(url):
    return requests.get(url)


def send_get_with_session(url, header):
    s = requests.Session()
    s.headers.update(header)
    return s.get(url)
