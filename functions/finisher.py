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

    database = Database(
        dynamodb_table,
        dynamodb_content,
        s3_bucket,
        s3_filename,
        s3_content
    )

    try:
        if event['action'] == 'PUT':
            database.save()

        elif event['action'] == 'UPDATE':
            database.update()

        # If everythings wen't okay it will return a 200 status code
        response['status_code'] = 200

    except DataRealError:
        response['status_code'] = 500

    return response
