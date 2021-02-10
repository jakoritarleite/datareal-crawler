from __future__ import annotations

import boto3
import multiprocessing
from json import dumps
from os import environ
from time import time, sleep
from datetime import datetime

from lib.request import librequest
from lib.database import scan_table
from lib.database import update_item
from lib.fake_headers import UserAgent

def run(event, content):
    """Docstring for online_checker.run function

    Args:
        param1 (str|None) event:LastEvaluatedKey:
            The key to the next page of the Table

    It will iter throught all db items and make a single request
    to see if the url is still alive, and then update the Db
    with the last status code and date.
    """
    lambda_client = boto3.client('lambda')
    response: dict = {'status': 200}
    start_key: str = event.get('LastEvaluatedKey')
    # If you want to set a limit to the returned items, add {'Limit': X} inside the dict function above
    # This is usefull so the Lambda function don't time out
    query = dict({'Limit': 10})

    if start_key:
        query['ExclusiveStartKey'] = start_key

    items, last_key = scan_table(environ.get('PROPERTIES_TABLE_NAME'), query)

    print('items_len', len(items))
    print('last_ley', last_key)

    processes: list = list()

    for item in items:
        start_time = time()

        _response = librequest.request(
            url=item['url'],
            method='GET',
            render=False,
            user_agent=f"User-Agent: {UserAgent().random()}",
            use_proxy=False)

        new_item = {
            'Key': {
                'id': item['id'],
                'url': item['url']
            },
            'Item': {
                'http': str(_response['status_code']),
                'date': datetime.today().strftime("%Y-%m-%d"),
                'last_http': {
                    'http': str(item['status']['http']),
                    'date': item['status']['date']
                }
            }
        }

        process = multiprocessing.Process(target=update_http_status, args=(new_item,))
        process.start()
        process.join()

        sleep(10)

    if last_key:
        lambda_client.invoke(
            FunctionName=environ.get('CHECKER_ARN'),
            InvocationType='Event',
            Payload=dumps({'LastEvaluatedKey': last_key})
        )

        response.update({
            'LastEvaluatedKey': last_key
        })

    return response
    
def update_http_status(new_item):
    print(f'{datetime.now().strftime("%H:%M:%S")} UpdateHttpStatus: {new_item["Key"]["id"]}')

    update_item(environ.get('PROPERTIES_TABLE_NAME'), new_item)