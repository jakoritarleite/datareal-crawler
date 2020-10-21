import re
import boto3
import requests
import tldextract

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

def get_xpath(table, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    _extractor = tldextract.TLDExtract(cache_file=False)
    _domain = _extractor(url)
    domain = f'{_domain.domain}.{_domain.suffix}'

    response = table.query(
        IndexName='domain-index',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('domain').eq(domain)
    )

    return response['Items'][0]
