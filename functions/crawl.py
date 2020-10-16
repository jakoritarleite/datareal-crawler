import os
import uuid
import json
import boto3
from parsel import Selector
from lib.utils import get_html
from urllib.parse import urljoin
from lib.utils import URL_validator
from lib.dispatcher import Dispatcher
from lib.utils import get_xpath_scrape

def run(event, context):
    print('crawl')

    crawlId     =   uuid.uuid4()
    next_page   =   event['next_page']
    mapping     =   event['mapping']
    url         =   event['url']
    dispatcher  =   Dispatcher(os.environ['SNS_JOBS_TOPIC_ARN'], crawlId)

    print(event)

    api_response = get_html(url)
    target_urls = find_target_urls(api_response, mapping, url)
    jobs = build_jobs(crawlId, target_urls)
    batches = dispatcher.send_batch(jobs)

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

    items = body.xpath(xpaths['item'])

    #target_urls = list(filter(None.__ne__, list(map(get_urls, items, [xpaths], [origin]))))

    target_urls = [ get_urls(item, xpaths, origin) for item in items ]

    print(f'Found ${len(target_urls)} matching targetUrls')

    return target_urls

def get_urls(item, xpaths, origin):
    url = item.xpath(xpaths['link']).extract_first()

    if url:
        if not URL_validator(url):
            url = urljoin(origin, url)

        return url

    else:
        return None

def build_jobs(crawlId, target_urls):
    jobs = list(map(lambda url: {"crawlId": str(crawlId), "url": url, "mapping": get_xpath_scrape(url)}, target_urls))

    print(f'Created ${len(jobs)} jobs for batch')

    return jobs