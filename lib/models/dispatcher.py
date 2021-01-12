from __future__ import annotations

from json import dumps
from time import sleep
from uuid import uuid4
from boto3 import client

from base64 import b64encode
from lib.compressor import compress

class Dispatcher:
    def __init__(
        self,
        machine_arn: str,
        execution_id: str = None,
        wait: bool = False,
        timeout: float = 0.0
    ):
        self.sfn = client('stepfunctions')
        self.machine_arn = machine_arn
        self.execution_id = execution_id
        self.wait = wait
        self.timeout = timeout

    def send_batch(self, jobs: List[Dict[str, str]]) -> List:
        response: List = list()
        
        if not jobs:
            raise Exception('Missing jobs for Dispatcher.send_batch')

        for job in jobs:
            response.append(
                self.send_job(job)
            )

        return response

    def send_job(self, job: Dict[str, str]) -> Response:
        if not job:
            raise Exception('Missing job for Dispatcher.send_job')

        if self.wait:
            print('Waiting to continue with the Process')
            sleep(self.timeout)

        response = self.sfn.start_execution(
            stateMachineArn=self.machine_arn,
            name=str(uuid4()),
            input=dumps(job)
        )

        return response

    def build_jobs(self, items: List[str, str]) -> List[Jobs]:
        jobs: List[Dict[str, str]] = list()

        for item in items:
            jobs.append(item)

        return jobs

    def build_finisher(
        self,
        execution_id: str,
        action: str,
        item: Dict[str, str],
        table: str,
        bucket: str = None,
        filename: str = None,
        file_content: bytes = None 
    ) -> List[Job]:
        job: List[Dict[str, str]] = list()
        struct: Dict[str, str] = {
            'executionId': execution_id,
            'action': action,
            'dynamo': {
                'table': table,
                'content': b64encode(dumps(item).encode('utf-8')).decode('utf-8')
            }
        }

        if bucket:
            struct.update({
                's3': {
                    'bucket': bucket,
                    'filename': filename,
                    'content': b64encode(compress(file_content)).decode()
                }
            })

        job.append(struct)

        return job

    def build_crawls(self, url, render):
        job: List[Dict[str, str]] = list()

        job.append({
            'url': url,
            'render': str(render).lower()
        })

        return job

    def build_verifier(self, urls, render):
        jobs: List[Dict[str, str]] = list()

        job: Dict[str, str] = {
            'executionId': self.execution_id,
            'urls': urls,
            'render': str(render).lower()
        }

        jobs.append(job)

        return jobs

    def build_dispatcher(self, urls, next_page, do_wait, wait_time, do_render = False):
        jobs: List[Dict[str, str]] = list() 

        job = {
            'executionId': self.execution_id,
            'scrape': urls,
            'crawls': next_page,
            'render': str(do_render).lower()
        }

        if do_wait == 'true':
            job.update({
                'wait': wait_time
            })

        jobs.append(job)

        return jobs