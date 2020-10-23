import json
import uuid
import boto3

sfn = boto3.client('stepfunctions')

class Dispatcher(object):
    def __init__(self, topicArn):
        self.response = []
        self.topicArn = topicArn

    def send_batch(self, jobs):
        print('Dispatcher.sendBatch()')

        if not jobs:
            raise Exception('Missing jobs for Dispatcher.sendBatch')

        for i in range(len(jobs)):
            self.response.append(self.send(jobs[i]))

        return self.response

    def send(self, job):
        print('Dispatcher.send()')

        if not job:
            raise Exception('Missing job for Dispatcher.send')

        response = sfn.start_execution(
            stateMachineArn=self.topicArn,
            name=str(uuid.uuid4()),
            input=json.dumps(job)
        )

        return response
