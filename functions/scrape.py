import os
import json
import uuid
from parsel import Selector
from lib.utils import get_html
from lib.event import parseEvent
from lib.models.crawls import Crawls

def run(event, context):
    print('scrape')

    scrapeId    =   uuid.uuid4()
    eventBody   =   parseEvent(event)
    crawlId     =   eventBody['payload']['crawlId'] or None
    mapping     =   eventBody['payload']['mapping']
    url         =   eventBody['payload']['url']
    crawls      =   Crawls(os.environ['CRAWLS_TABLE_NAME'], crawlId, scrapeId)

    api_response = get_html(url)

    body = Selector(text=api_response.text.strip())

    title = body.xpath(mapping['title']).extract_first()
    price = body.xpath(mapping['price']).extract_first()

    item = {
        'title': title,
        'price': price
    }

    crawls.save(item)
    crawls.find()

    response = {
        "id": scrapeId.hex,
        "statusCode": api_response.status_code,
        "body": json.dumps(item)
    }

    return response
