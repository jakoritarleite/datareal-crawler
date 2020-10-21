import json
import boto3

dynamodb = boto3.resource('dynamodb')

class Crawls(object):
    def __init__(self, table, crawlId = None):
        self.table = dynamodb.Table(table)
        self.crawlId = crawlId

    def find(self):
        print(f'Crawls.find({self.crawlId})')

        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(str(self.crawlId))
        )

        return [ response['Items'][i]['data'] for i in range(len(response['Items'])) ] 


    def save(self, data):
        print('Crawls.save()')

        self.table.put_item(Item=data)
