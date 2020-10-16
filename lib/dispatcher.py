import json
import boto3

sns = boto3.client('sns')

class Dispatcher(object):
    def __init__(self, topicArn, crawlId):
        self.topicArn = topicArn
        self.crawlId = crawlId

    def send_batch(self, jobs):
        print('Dispatcher.sendBatch()')

        if not jobs:
            raise Exception('Missing jobs for Dispatcher.sendBatch')

        return list(map(self.send, jobs))

    def send(self, job):
        print('Dispatcher.send()')
        print(job)

        if not job:
            raise Exception('Missing job for Dispatcher.send')

        response = sns.publish(
            TopicArn=self.topicArn,    
            Message=str(job),    
        )
        
        return response