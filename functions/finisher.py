"""
    Receives a dict from the Scrape Spider with
    the crawled information to save on DynamoDB,
    and maybe it receives the html body to save on S3.

    The dict may look like this:
    -  {
        'executionId': HASH,
        'action': 'UPDATE/PUT'
        'dynamo': {
            'table': ...,
            ...
        },
        's3': {                 // This may not be in the dict, depends if the body already exists on the S3 bucket
            'bucket': ...,
            'filename': ...,
            'content': ...
        }
    }
"""
from json import loads
from base64 import b64decode
from datetime import datetime

from lib.compressor import decompress
from lib.exceptions import DataRealError
from lib.models.database import Database

def run(event, context):
    executionId = event['executionId']
    response: dict = {'id': executionId}

    dynamodb_table = event['dynamo']['table']
    dynamodb_content = loads(b64decode(event['dynamo']['content'].encode('utf-8')).decode('utf-8'))

    s3_bucket: str = None
    s3_filename: str = None
    s3_content: bytes = None

    if 's3' in event:
        s3_bucket = event['s3']['bucket']
        s3_filename = event['s3']['filename']
        s3_content = decompress(b64decode(event['s3']['content'].encode()))

    database_crawls = Database(
        dynamodb_table,
        dynamodb_content,
        s3_bucket,
        s3_filename,
        s3_content
    )
    database_crawls.save()

    dynamodb_properties_content = dynamodb_content
    dynamodb_properties_content['id'] = dynamodb_properties_content['scrapeId']
    dynamodb_properties_content['status'] = loads(event['dynamo']['http_status'])

    del dynamodb_properties_content['date']
    del dynamodb_properties_content['scrapeId']

    # This is required to bypass ValidationException when saving in DynamoDB
    # ValidationException is raised when you try to PutItem/UpdateItem an item with Null or whatever type
    # which was expected to be another thing
    for key in dynamodb_properties_content:
        if dynamodb_properties_content[key] == None:
            dynamodb_properties_content[key] = 'Undefined'

        if not key in ['features', 'images', 'status']:
            dynamodb_properties_content[key] = str(dynamodb_properties_content[key])

    database_properties = Database(
        'datareal-crawler-dev-properties',
        dynamodb_properties_content
    ) 

    try:
        if event['action'] == 'PUT':
            database_properties.save()

        elif event['action'] == 'UPDATE':
            database_properties.update()

        # If everythings wen't okay it will return a 200 status code
        response['status_code'] = 200

    except DataRealError:
        response['status_code'] = 500

    return response
