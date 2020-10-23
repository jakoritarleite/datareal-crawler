import os
import uuid
import json
import boto3
from parsel import Selector
from lib.utils import get_html
from lib.utils import get_xpath
from lib.event import parseEvent
from urllib.parse import urljoin
from lib.utils import URL_validator
from lib.dispatcher import Dispatcher

def run(event, context):
    print('crawl')

    crawlId     =   uuid.uuid4()
    eventBody   =   parseEvent(event)
    url         =   eventBody['payload']['url']
    mapping     =   get_xpath('datareal-crawler-dev-crawls-config', url)
    dispatcher  =   Dispatcher(os.environ['SCRAPE_ARN'])

    print(event)

    api_response    = get_html(url)
    
    target_urls     = find_target_urls(api_response, mapping, url)
    jobs            = build_jobs_scrape(crawlId, target_urls)
    batches         = dispatcher.send_batch(jobs)

    if batches:
        print('Scrape jobs dispatched successfuly!')

        response = {
            "statusCode": 200,
            "body": json.dumps({'id': str(crawlId)})
        }

        return response

    else:
        print('Something wrent wrong when dispatching jobs')

        response = {
            "statusCode": 500,
            "body": json.dumps({'id': str(crawlId)})
        }

        return response

def find_target_urls(response, xpaths, origin):
    body = Selector(text=response.text.strip())

    items = body.xpath(xpaths['parser_items'])

    target_urls = [ get_urls(item, xpaths, origin) for item in items ]

    print(f'Found ${len(target_urls)} matching targetUrls')

    return target_urls

def get_urls(item, xpaths, origin):
    url = item.xpath(xpaths['parser_items_url']).extract_first()

    if url:
        if not URL_validator(url):
            url = urljoin(origin, url)

        return url

def build_jobs_scrape(crawlId, target_urls):
    jobs = [ {"crawlId": str(crawlId), "url": str(target_urls[i])} for i in range(len(target_urls))]

    print(f'Created ${len(jobs)} jobs for batch')

    return jobs