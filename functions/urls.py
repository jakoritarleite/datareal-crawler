from os import environ
from re import findall
from uuid import uuid4
from json import dumps
from parsel import Selector
from lib.xpath import get_xpath
from lib.dispatcher import Dispatcher
from lib.models.request import Request

def run(event, context):
    print('urls')

    urlsId      = uuid4()
    url         = event['url']
    mapping     = get_xpath('datareal-crawler-dev-crawls-config', url)
    dispatcher  = Dispatcher(environ['CRAWLS_ARN'], mapping['parser_arguments_wait'], mapping['parser_arguments_wait_time'])

    print(event)

    api_response = Request(url=url, render=mapping['parser_arguments_render']).fetch()
    target_pages = find_target_pages(api_response, mapping, url)
    crawls_jobs  = build_jobs_crawls(target_pages)
    crawls_batches = dispatcher.send_batch(crawls_jobs)

    if crawls_batches:
        print('Crawls jobs dispatched successfuly!')

        response = {
            "statusCode": 200,
            "body": dumps({'id': str(urlsId)})
        }

        return response

    else:
        print('Something wrent wrong when dispatching jobs')

        response = {
            "statusCode": 500,
            "body": dumps({'id': str(urlsId)})
        }

        return response

def add_iter_url(url, page_str, value) -> str:
    return f'{url}{page_str}{value}'

def find_target_pages(response, xpaths, url):
    body = Selector(text=response.content.decode('utf-8'))
    pages = None
    _pages = []

    if xpaths['parser_next_page'] != "false":
        if xpaths['parser_next_page'].endswith('/text()'):
            pages = findall(r'\d+', body.xpath(xpaths['parser_next_page']).extract_first())

        else:
            pages = body.xpath(xpaths['parser_next_page']).extract()

        try:
            for i in range(int(pages[0]) if isinstance(pages, list) else int(pages)):
                _pages.append(add_iter_url(url, xpaths['parser_url_string'], i + 1))

        except Exception as error:
            print('Error after for i range(pages)')
            print(error)

    return _pages

def build_jobs_crawls(target_pages):
    jobs = [ {"url": target_pages[i]} for i in range(len(target_pages)) ]

    print(f'Created ${len(jobs)} jobs for batch')

    return jobs