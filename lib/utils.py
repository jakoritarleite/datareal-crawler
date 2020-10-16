import re
import requests

def URL_validator(url): # DJango URL Validator
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None

def get_html(url):
    payload = {'api_key': 'c99f7077da80e3cebb9f29e288ac87e8', 'url': url, 'render': 'true'}
    response = requests.get('http://api.scraperapi.com', params=payload)

    return response

def get_xpath_scrape(url):
    mapping = {
        "title": "//div[@class='conteudo']/div[contains(@class,'faixa-cinza')]/div[@class='centraliza']/h2[@class='tit-imovel']/text()",
        "price": "//div[@class='conteudo']/div[@class='centraliza']/span[@class='valor-padrao' and not(//div[@class='conteudo']/div[@class='centraliza']/span[@class='valor-atual'])]/strong[@class='valor']/text()"
    }

    return mapping