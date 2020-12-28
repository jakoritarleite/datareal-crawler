from __future__ import annotations

from os import environ

from lib.models.database import S3Utils
from lib.models.database import DynamoUtils
from lib.models.dispatcher import Dispatcher

def run(event, context) -> Dict[str, str]:
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
                'urls': ['http...',...],
                'useS3Content': true/false (optional),
                'render': 'true/false' (optional)
            }

    Returns:
        Object with status code 200 if everything went ok
        and if something goes wrong it returns another statue code
    """
    execution_id = event['executionId']
    response: Dict[str, str] = {'id': execution_id}
    use_s3: bool = False
    jobs: List = list()
    s3_objects = List = list()
    dynamo_objects = List = list()
    jobs: List = list()
    do_render: bool = False

    if 'render' in event and event['render'].lower() == 'true':
        do_render = True

    dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['SCRAPE_ARN'],
        execution_id=execution_id
    )

    if 'useS3Content' in event and event['useS3Content'].lower() == 'true':
        use_s3 = True

    for url in event['urls']:
        job: Dict[str, str] = dict({'url': url, 'saveS3': 'true', 'render': str(do_render).lower()})

        if use_s3:
            s3_object = S3Utils.get_filename_from_url(url)
            s3_func = S3Utils(
                s3_bucket='datareal-crawler-bodies',
                s3_path=s3_object['folder'],
                s3_filename=s3_object['file']
            )

            if s3_func.verify():
                job.update(
                    {
                        'content': s3_func.download()
                    }
                )

"""This commented code block is for when you want to update the existent items on Db with the new ones    
        if dynamo_object := DynamoUtils(environ['CRAWLS_TABLE_NAME']).get(
            {
                'index': 'url-index',
                'key': 'url',
                'value': url
            }
        ):
            print('The URL is already on Dynamo Table')

            if len(dynamo_object) > 1:
                for obj in dynamo_object[1:]:
                    print('Deleting duplicated URLs')
                    DynamoUtils(environ['CRAWLS_TABLE_NAME']).delete(
                        {
                            'partition_key': 'id',
                            'sort_key': 'scrapeId',
                            'id': obj['id'],
                            'scrapeId': obj['scrapeId']
                        }
                    )

            job.update({
                'executionId': dynamo_object[0]['id'],
                'scrapeId': dynamo_object[0]['scrapeId'],
                'action': 'UPDATE'
            })

        else:
            print('The URL do not exists on Dynamo Table') """
        job.update({
            'executionId': execution_id,
            'scrapeId': None,
            'action': 'PUT'
        })
        jobs.append(job)

    sent = dispatcher.send_batch(jobs)

    if sent:
        response.update({
            'status_code': 200,
            'status_machine_arn': environ['SCRAPE_ARN']
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