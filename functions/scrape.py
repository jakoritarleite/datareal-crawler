import os
import json
import uuid
from parsel import Selector
from lib.utils import get_html
from lib.utils import get_xpath
from lib.event import parseEvent
from lib.models.crawls import Crawls

def run(event, context):
    print('scrape')

    scrapeId    =   uuid.uuid4()
    eventBody   =   parseEvent(event)
    crawlId     =   eventBody['payload']['crawlId'] if 'crawlId' in eventBody['payload'] else None
    url         =   eventBody['payload']['url']
    mapping     =   get_xpath('datareal-crawler-dev-scrape-config', url)
    crawls      =   Crawls(os.environ['CRAWLS_TABLE_NAME'])

    api_response = get_html(url)

    body = Selector(text=api_response.text.strip())

    images = {}
    images['src'] = body.xpath(mapping['parser_images_src']).extract()
    images['alt'] = body.xpath(mapping['parser_images_alt']).extract()

    item = {
        'id':       str(crawlId) if crawlId else str(scrapeId),
        'scrapeId': str(scrapeId),
        'url':      url,
        'title':    body.xpath(mapping['parser_title']).extract_first(),
        'category': body.xpath(mapping['parser_category']).extract_first(),
        'price':    body.xpath(mapping['parser_price']).extract_first(),
        'rooms':    body.xpath(mapping['parser_rooms']).extract_first(),
        'suites':   body.xpath(mapping['parser_suites']).extract_first(),
        'garages':  body.xpath(mapping['parser_garages']).extract_first(),
        'location': body.xpath(mapping['parser_location']).extract_first(),
        'features': body.xpath(mapping['parser_features']).extract_first(),
        'body':     body.xpath(mapping['parser_body']).extract_first(),
        'images':   [ { 'src': images['src'][i], 'alt': images['alt'][i] } for i in range(len(images['src'])) ]
    }

    crawls.save(item)

    response = {
        "id":           str(scrapeId),
        "statusCode":   api_response.status_code,
        "body":         json.dumps(item)
    }

    return response
