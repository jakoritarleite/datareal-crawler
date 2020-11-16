from __future__ import annotations

from os import environ

from lib.models.dispatcher import Dispatcher

def run(event, context) -> Dict[str, int]:
    """Docstring for the run function.

    Receives a dict from the Crawl State Machine
    with the executionId (crawlId) and the urls to
    be send to Scrape and next page that will be
    send to Crawl

    Args:
        param1 (obj) event:
            The object:dict with executionId, scrape urls and crawl next_page
        param2 (obj) context:
            The object:dict with the AWS::Lambda::State configurations
    
    Examples:
        The param1 should look this this:
            {
                'executionId': HASH,
                'scrape': ['http...',...],
                'crawls': 'https:...next_page',
                'wait': time_to_wait (optional)
            }

    Returns:
        Object with status code 200 if everything went ok
        and if something goes wrong it returns another statue code
    """
    execution_id = event['executionId']
    response: Dict[str, str] = {'id': execution_id}
    crawls_dispatcher: ClassVar[Dispatcher]
    verifier = event['scrape']
    wait: bool = False
    timeout: float = 0.0

    if 'wait' in event:
        wait = True
        timeout = float(event['wait'])

    verifier_dispatcher: ClassVar[Dispatcher] = Dispatcher(
        machine_arn=environ['VERIFIER_ARN'],
        execution_id=execution_id,
        wait=wait,
        timeout=timeout
    )

    crawls_dispatcher = Dispatcher(
        machine_arn=environ['CRAWLS_ARN'],
        wait=wait,
        timeout=timeout
    )

    if 'crawls' in event:
        crawls_job = crawls_dispatcher.build_crawls(event['crawls'])
        crawls_response = crawls_dispatcher.send_batch(crawls_job)

        response.update({
            'crawls': 'OK'
        })

    verifier_job = verifier_dispatcher.build_verifier(verifier)
    verifier_response = verifier_dispatcher.send_batch(verifier_job)

    if verifier_response:
        response.update({
            'verifier': 'OK'
        })

    return response