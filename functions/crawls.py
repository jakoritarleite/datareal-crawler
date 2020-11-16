from __future__ import annotations

from os import environ
from uuid import uuid4

from lib.models.crawl import Crawl
from lib.models.dispatcher import Dispatcher

from lib.xpath import get_xpaths
from lib.html import get_from_url

def run(event, context) -> Dict[str, str]:
    """Docstring for crawls.run function.

    It crawl for items on real state search page and
    the next page url, then sends it to the dispatcher
    state machine

    Args:
        param1 (obj) event:
            The object:dict with the url
        param2 (obj) context:
            The object:dict with the AWS::Lambda::State configuration

    Examples:
        The param1 should look like this:
            {
                'url': 'https://www.example.com',
                'saveS3: 'true/false' (optional)
            }

    Returns:
        Object with status code 200 if everything went ok
        and if somethings goes wrong it returns another status code
    """
    execution_id: str = str(uuid4())
    url: str = event['url']
    save_s3: bool
    response: Dict[str, str] = {'id': execution_id}
    result: Dict[str, str] = {'id': execution_id}
    html: bytes = get_from_url(event['url'])
    parser: ClassVar[T]

    if 'saveS3' in event:
        if event['saveS3'].lower() == 'true':
            response.update({'saveS3': event['saveS3']})

        elif event['saveS3'].lower() == 'false':
            response.update({'saveS3': event['saveS3']})

        else:
            raise Exception('The saveS3 key must be True or False, anything other than that will raise a Error.')
 
    xpaths: dict[str, str] = get_xpaths(
        table=environ['CRAWLS_XPATH'],
        url=event['url']
    )

    parser = Crawl(
        mapping=xpaths,
        use_scrape=False,
        use_head=False,
    )

    urls, next_page = parser.get_content(content=html, url=event['url'])

    dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['DISPATCHER_ARN'],
        execution_id=execution_id
    )

    dispatcher_job = dispatcher.build_dispatcher(urls, next_page, xpaths['parser_arguments_wait'], xpaths['parser_arguments_wait_time'])
    dispatcher_response = dispatcher.send_batch(dispatcher_job)

    if dispatcher_response:
        response.update({
            'status_code': 200
        })

    else:
        response.update({
            'status_code': 500
        })

    return response