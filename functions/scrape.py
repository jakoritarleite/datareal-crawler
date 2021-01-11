from __future__ import annotations

from os import environ
from uuid import uuid4

from lib.models.crawl import Crawl
from lib.sanitizer import Sanitizer
from lib.models.dispatcher import Dispatcher

from lib.models.database import S3Utils

from lib.xpath import get_xpaths
from lib.html import get_from_url, get_from_body

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
                'scrapeId': HASH (MAY NOT BE HERE),
                'action': 'UPDATE/PUT',
                'url': 'https://www.example.com',
                'url': 's3://datareal-crawler-bodies/{md5(domain)}}/{md5(path)}/date.body',
                'content': '<html>...' (MAY NO BE HERE)
            }

    Returns:
        Object with status code 200 if everything went ok
        and if something goes wrong it returns another statue code
    """
    execution_id = event['executionId']
    scrape_id = event['scrapeId'] or str(uuid4())
    save_s3 = event['saveS3']
    response: Dict[str, str] = {'id': execution_id, 'scrapeId': scrape_id}
    result: Dict[str, str] = {'id': execution_id, 'scrapeId': scrape_id}
    html: bytes
    parser: ClassVar[T]
    use_head: bool = False
    do_render: bool = False

    if 'render' in event and event['render'].lower() == 'true':
        do_render = True

    dispatcher_price_verifier: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['PRICE_VERIFIER_ARN'],
        execution_id=execution_id
    )

    dispatcher_finisher: ClassVar[Dispatcher] = Dispatcher(
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
    snt = Sanitizer(content)
    content_cleansed = snt.clean()

    result.update(content_cleansed)

    s3_bucket: str = None
    s3_path: str = None
    s3_file: str = None

    if save_s3.lower() == 'true':
        s3_bucket = 'datareal-crawler-bodies'
        s3_object = S3Utils.get_filename_from_url(url=event['url'])

        s3_folder = s3_object['folder']
        s3_file = s3_object['file']
        s3_path = f'{s3_folder}/{s3_file}'

    jobs_pv = dispatcher_price_verifier.build_finisher(execution_id=execution_id, action=event['action'], item=result, table=environ['CRAWLS_TABLE_NAME'])
    sent_pv = dispatcher_price_verifier.send_batch(jobs_pv)

    jobs_fn = dispatcher_finisher.build_finisher(execution_id=execution_id, action=event['action'], item=result, table=environ['CRAWLS_TABLE_NAME'], bucket=s3_bucket, filename=s3_path, file_content=html)
    sent_fn = dispatcher_finisher.send_batch(jobs_fn)

    if sent_pv and sent_fn:
        response.update({
            'status_code': 200,
            'state_machine_arn': environ['FINISHER_ARN']
        })

    else:
        response.update({
            'status_code': 500
        })

    for item in content:
        if item == 'images' or item == 'features':
            print(f"'{item}': len<{len(content[item])}>")
        else:
            print(f"'{item}': '{str(content[item]).strip()}'")

    print(f'next_machine_response:\n{sent_fn}\n{sent_pv}')

    return response
