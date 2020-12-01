"""
    Objects that allow you to get items from S3 and DynamoDB

    :param s3_bucket: Name of the target bucket name
    :param s3_path: The sub-folder path to the file
    :param s3_filename: THe name of the file
"""

from __future__ import annotations

import os
import boto3
import hashlib

from io import BytesIO
from base64 import b64encode
from io import open as openIO
from botocore import exceptions
from boto3.dynamodb import conditions
from lib.url import extract_domain, extract_path

class S3Utils:
    def __init__(self, s3_bucket: str, s3_path: str, s3_filename: str) -> None:
        self.s3_path = s3_path
        self.s3_filename = s3_filename
        self.s3_bucket = s3_bucket

        assert isinstance(self.s3_bucket, str), \
            'The S3 Bucket name must be String'

        assert isinstance(self.s3_path, str), \
            'The S3 sub-folder must be String'

        assert isinstance(self.s3_filename, str), \
            'The S3 filename must be String'

        self.s3 = boto3.resource('s3')

    @staticmethod
    def get_filename_from_url(url: str) -> Dict[str, str]:
        """
        md5(domain)/md5(url[domain:])
        """
        response: Dict[str, str] = dict()

        domain = extract_domain(url=url)
        path = extract_path(url=url)

        folder = hashlib.md5(domain.encode()).hexdigest()
        file = hashlib.md5(path.encode()).hexdigest()

        response.update({
            'folder': folder,
            'file': file + '.body'
        })

        return response

    def download(self) -> bytes:
        content: bytes

        bucket = self.s3.Bucket(self.s3_bucket)

        try:
            with openIO(f'/tmp/{self.s3_filename}', 'wb') as file:
                bucket.download_fileobj(f'{self.s3_path}/{self.s3_filename}', file)
            
            with openIO(f'/tmp/{self.s3_filename}', 'rb') as file:
                content = file.read()

            os.remove(f'/tmp/{self.s3_filename}')

        except exceptions.ClientError as error:
            print(error)
            raise Exception('Something went wrong downloading file in S3 Bucket.')

        return b64encode(content).decode('utf-8')

    def verify(self) -> bool:
        response: bool
        
        try:
            obj = self.s3.Object(bucket_name=self.s3_bucket, key=f'{self.s3_path}/{self.s3_filename}').get()

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                response = False

            else:
                print(error)
                raise Exception('Something went wrong searching for file in S3 Bucket.')
        else:
            response = True

        return response

class DynamoUtils:
    def __init__(self, dynamo_table: str):
        self.dynamo_table = dynamo_table

        assert isinstance(self.dynamo_table, str), \
            'DynamoDB Table must be String'

        self.dynamo = boto3.resource('dynamodb')
        self.table = self.dynamo.Table(self.dynamo_table)

    def get(self, query: dict) -> dict:
        try:
            response = self.table.query(
                IndexName=query['index'],
                KeyConditionExpression=conditions.Key(query['key']).eq(query['value'])
            )

        except exceptions.ClientError as error:
            print(error.response['Error']['Message'])

        else:
            for item in response['Items']:
                if item['last_check'] == 'true':
                    return item