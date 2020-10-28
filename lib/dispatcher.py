from json import dumps
from time import sleep
from uuid import uuid4
from boto3 import client

sfn = client('stepfunctions')

class Dispatcher(object):
    def __init__(self, topicArn, wait=False, timeout=0):
        self.wait = bool(wait)
        self.response = []
        self.timeout = int(float(timeout))
        self.topicArn = topicArn

    def send_batch(self, jobs):
        print('Dispatcher.sendBatch()')

        if not jobs:
            raise Exception('Missing jobs for Dispatcher.sendBatch')

        for i in range(len(jobs)):
            if self.wait:
                self._wait(self.timeout)

            self.response.append(self.send(jobs[i]))

        return self.response

    def send(self, job):
        print('Dispatcher.send()')

        if not job:
            raise Exception('Missing job for Dispatcher.send')

        response = sfn.start_execution(
            stateMachineArn=self.topicArn,
            name=str(uuid4()),
            input=dumps(job)
        )

        return response

    def _wait(self, timeout):
        if not timeout: pass
        else: sleep(timeout)
