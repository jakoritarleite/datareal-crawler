from __future__ import annotations

from uuid import uuid4
from os import environ
from json import loads
from base64 import b64decode
from base64 import b64encode
from datetime import datetime

from lib.url import extract_domain
from lib.models.database import DynamoUtils
from lib.models.dispatcher import Dispatcher

def run(event, context) -> Dict[str, str]:
    """Docstring for price_verifier:run function

    Receives a dict from the Scrape Spider with
    the crawled information to check if there is any
    price variation, if has variation it sends that
    to the Finisher within Scrape Information

    The received dict may look like this:
    -  {
        'executionId': HASH,
        'dynamo': {
            'table': ...,
            ...
        },
        's3': {                 // This may not be in the dict, depends if the body already exists on the S3 bucket
            'bucket': ...,
            'filename': ...,
            'content': ...
        }
    }
    """
    response: Dict[str, str] = {'id': event['executionId']}
    price_variation: Dict[str, str] = {'id': str(uuid4())}
    current_date: Date = datetime.now()
    content: Dict[str, str] = loads(b64decode(event['dynamo']['content'].encode()).decode())
    price_verifier: ClassVar = DynamoUtils(environ['PRICE_VARIATION'])
    check: Dict[str, str] = None

    check_objects = price_verifier.get(
        {
            'index': 'url-index', 
            'key': 'url', 
            'value': content['url']
        }
    )

    for item in check_objects:
        if item['last_check'] == 'true':
            check = item

    if check:
        print(f"The following URL already exists on the Database: [{content['url']}]")

        if content['price'] == check['price']:
            print('The last check price is the same as today.')

        else:
            price_variation.update(
                {
                    'year': current_date.strftime('%Y'),
                    'month': current_date.strftime('%m'),
                    'day': current_date.strftime('%d'),
                    'last_check': 'true',
                    'url': content['url'],
                    'price': content['price'],
                    'domain': check['domain']
                }
            )

            # Update the current price status[last_check] on DynamoDB to false
            updater_response = price_verifier.update(
                {
                    'partition_key': 'id',
                    'sort_key': 'url',
                    'id': check['id'],
                    'url': check['url'],
                    'target': 'last_check',
                    'value': 'false'
                }
            )

            price_verifier.put(item=price_variation)

            print('Updater Response:', updater_response)
            print('New Price Item:', price_variation)

    else:
        price_variation.update(
            {
                'year': current_date.strftime('%Y'),
                'month': current_date.strftime('%m'),
                'day': current_date.strftime('%d'),
                'last_check': 'true',
                'url': content['url'],
                'price': content['price'],
                'domain': extract_domain(content['url'])
            }
        )

        price_verifier.put(item=price_variation)

        print('Added the URL to the Price Variation Table', price_variation)
