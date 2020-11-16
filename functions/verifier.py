from __future__ import annotations

from os import environ
from base64 import b64decode

from lib.models.database import S3Utils
from lib.models.dispatcher import Dispatcher

def run(event, context) -> Dict[str, int]:
    """Docstring for the run function.

    Receives a dict from the Dispatcher State Machine
    with the executionId (crawlId) and the urls that
    will be searched on S3 to see if it's already
    saved, then, if the url is saved there it will
    send the content from the corresponding S3 file
    to Scrape, else, it will send the url to be scraped.
    
    Args:
        param1 (obj) event:
            The object:dict with executionId, scrape urls and crawl next_page
        param2 (obj) context:
            The object:dict with the AWS::Lambda::State configurations
    
    Examples:
        The param1 should look this this:
            {
                'executionId': HASH,
                'urls': ['http...',...]
            }

    Returns:
        Object with status code 200 if everything went ok
        and if something goes wrong it returns another statue code
    """
    execution_id = event['executionId']
    response: Dict[str, str] = {'id': execution_id}
    s3_objects = List = list()
    jobs: List = list()

    dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['SCRAPE_ARN'],
        execution_id=execution_id
    )

    for url in event['urls']:
        s3_object = S3Utils.get_filename_from_url(url)
        print(s3_object)

        s3_objects.append({
            'url': url,
            's3': S3Utils(
                s3_bucket='datareal-crawler-bodies',
                s3_path=s3_object['folder'],
                s3_filename=s3_object['file']
            )
        })

    for s3_object in s3_objects:
        job: dict = dict()
        content: bytes

        if s3_object['s3'].verify():
            content = s3_object['s3'].download()
            job = {
                'executionId': execution_id,
                'url': s3_object['url'],
                'content': content,
                'saveS3': 'false'
            }
        else:
            job = {
                'executionId': execution_id,
                'url': s3_object['url'],
                'saveS3': 'true'
            }

        jobs.append(job)

    sent = dispatcher.send_batch(jobs)

    if sent:
        response.update({
            'status_code': 200,
            'state_machine_arn': environ['SCRAPE_ARN']
        })

    else:
        response.update({
            'status_code': 500
        })
    
    print(
        'next_machine_response:\n',
        sent
        )

    return response