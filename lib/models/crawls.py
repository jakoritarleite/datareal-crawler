import json
import boto3

dynamodb = boto3.resource('dynamodb')

class Crawls(object):
    def __init__(self, table, crawlId, scrapeId = None):
        self.table = dynamodb.Table(table)
        self.crawlId = crawlId
        self.scrapeId = scrapeId

    def find(self):
        print(f'Crawls.find({self.crawlId})')

        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(str(self.crawlId))
        )

        return list(map(lambda x: json.loads(x['data']), response['Items']))


    def save(self, data):
        print('Crawls.save()')

        item = {
            'id': str(self.crawlId) or str(self.scrapeId),
            'scrapeId': str(self.scrapeId),
            'data': json.dumps(data, separators=(',', ':'))
        }

        self.table.put_item(Item=item)
