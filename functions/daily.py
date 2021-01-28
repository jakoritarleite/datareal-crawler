from os import getenv
from json import dumps

from lib.models.dispatcher import Dispatcher

def run(event, context):
    urls = event['urls']

    dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=getenv('CRAWLS_ARN')
    )

    dispatcher_response = dispatcher.send_batch(urls)

    if dispatcher_response:
        print(dispatcher_response)

    return {
        'status_code': 200,
        'sent_urls': urls
    }