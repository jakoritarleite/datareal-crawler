from __future__ import annotations

from os import environ
from uuid import uuid4

from lib.models.crawl import Crawl
from lib.models.dispatcher import Dispatcher

from lib.models.database import S3Utils
from lib.models.database import DynamoUtils

from lib.xpath import get_xpaths
from lib.html import get_from_url
from lib.html import get_from_body

def run(event, context) -> Dict[str, int]:
    """Docstring for the run function.

    Receives a dict from the Dispatcher State Machine
    with the executionId (crawlId) and the url or the
    html body from s3 to be scraped.

    Note:
        The executionId and url/domain will always be present
        but content may not be in the object.
    
    Args:
        param1 (obj) event:
            The object:dict with executionId, url and maybe content
        param2 (obj) context:
            The object:dict with the AWS::Lambda::State configurations
    
    Examples:
        The param1 should look like this:
            {
                'executionId': HASH,
                'url': 'https://www.example.com',
                'url': 's3://datareal-crawler-bodies/{md5(domain)}}/{md5(path)}.body',
                'content': '<html>...'
                'saveS3': 'true/false'
            }

    Returns:
        Object with status code 200 if everything went ok
        and if something goes wrong it returns another statue code
    """
    execution_id = event['executionId']
    scrape_id = str(uuid4())
    save_s3 = event['saveS3']
    response: Dict[str, str] = {'id': execution_id, 'scrapeId': scrape_id}
    result: Dict[str, str] = {'id': execution_id, 'scrapeId': scrape_id}
    html: bytes
    parser: ClassVar[T]
    use_head: bool = False
    check_price: ClassVar[DynamoUtils] = None
    do_render: bool = False

    if 'render' in event and event['render'].lower() == 'true':
        do_render = True

    dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['FINISHER_ARN'],
        execution_id=execution_id
    )

    if 'content' in event:
        html = get_from_body(event['content'])

    else:
        html = get_from_url(event['url'], do_render)

    if 'olx' in event['url']:
        use_head = True

    xpaths: dict[str, str] = get_xpaths(
        table=environ['SCRAPE_XPATH'],
        url=event['url']
    )

    parser = Crawl(
        mapping=xpaths,
        use_scrape=True,
        use_head=use_head
    )

    content: Dict[str, str] = parser.get_content(content=html, url=event['url'])

    print('Returned content:',
        content)

    result.update(content)

    s3_bucket: str = None
    s3_path: str = None
    s3_file: str = None

    if save_s3.lower() == 'true':
        s3_bucket = 'datareal-crawler-bodies'

        s3_object = S3Utils.get_filename_from_url(url=event['url'])

        s3_folder = s3_object['folder']
        s3_file = s3_object['file']

        s3_path = f'{s3_folder}/{s3_file}'


    jobs = dispatcher.build_finisher(execution_id=execution_id, item=result, table=environ['CRAWLS_TABLE_NAME'], bucket=s3_bucket, filename=s3_path, file_content=html)

    sent = dispatcher.send_batch(jobs)

    if sent:
        response.update({
            'status_code': 200,
            'state_machine_arn': environ['FINISHER_ARN']
        })

    else:
        response.update({
            'status_code': 500
        })

    print(f'next_machine_response:\n{sent}')

    return response
