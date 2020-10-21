import json
import boto3

sns = boto3.client('sns')

class Dispatcher(object):
    def __init__(self, topicArn):
        self.topicArn = topicArn

    def send_batch(self, jobs):
        print('Dispatcher.sendBatch()')

        if not jobs:
            raise Exception('Missing jobs for Dispatcher.sendBatch')

        return [ self.send(jobs[i]) for i in range(len(jobs)) ]

    def send(self, job):
        print('Dispatcher.send()')

        if not job:
            raise Exception('Missing job for Dispatcher.send')

        response = sns.publish(
            TopicArn=self.topicArn,    
            Message=json.dumps(job),    
        )
        
        return response