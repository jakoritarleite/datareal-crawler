from __future__ import annotations

import boto3
from io import BytesIO

class Database:
    """Docstring for Database class.
    
    Creates the Database object to store on DynamoDB and S3.
    """
    def __init__(
        self,
        dynamodb_table: str = None,
        dynamodb_content: dict = None,
        s3_bucket: str = None,
        s3_filename: str = None,
        s3_content: bytes = None
    ) -> None:
        """Docstring fir tge __init__ method.
        Args:
            param1 (str) dynamodb_table:
                Name of the table to store the content on DynamoDB
            param2 (str) dynamodb_content:
                The content (dict) to be saved on Dynamo
            param3 (str) s3_bucket:
                Name of the bucket
            param4 (str) s3_filename:
                Name of the file that will be stored on S3
            param5 (str) s3_content:
                The content of the file
        """
        self.dynamodb_table = dynamodb_table
        self.dynamodb_content = dynamodb_content
        self._set_dynamo()

        self.s3_bucket = s3_bucket
        self.s3_filename = s3_filename
        self.s3_content = s3_content 

        # The body will not be saved on S3 if the variable is not a string
        if isinstance(self.s3_bucket, str):
            self._set_s3()

    def _set_dynamo(self) -> ClassVar[Dynamo]:
        """Docstring for the _set_dynamo property.

        Returns:
            ClassVar for the DynamoDB instance
        """
        self._dynamo = _Dynamo(self.dynamodb_table, self.dynamodb_content)

    def _set_s3(self) -> ClassVar[S3]:
        """Docstring for the _set_s3 property.

        Returns:
            ClassVar for the S3 instance
        """
        self._s3 = _S3(self.s3_bucket, self.s3_filename, self.s3_content)

    def save(self) -> None:
        """Docstring the save function.

        Save the content on Dynamo and S3 (If wanted)
        """
        if self.s3_bucket:
            self._s3._save()

        print('Trying to save on DynamoDB')
        print(self._dynamo)
        self._dynamo._save()

class _Dynamo:
    # TODO:
    # 1 - Create Class docstring
    # 2 - Create __init__ docstring
    # 3 - Create _save docstring
    def __init__(self, table, content) -> None:
        self.client = boto3.resource('dynamodb')
        self.table = self.client.Table(table)
        self.content = content

    def _save(self):
        print('Saving information on DYDB')
        self.table.put_item(Item=self.content)
        print('Saved on DynamoDB')

class _S3:
    # TODO:
    # 1 - Create Class docstring
    # 2 - Create __init__ docstring
    # 3 - Create _save docstring
    def __init__(self, bucket, filename, content) -> None:
        self.client = boto3.client('s3')

        self.bucket = bucket
        self.filename = filename
        self.content = BytesIO(content)

    def _save(self):
        self.client.upload_fileobj(self.content, self.bucket, self.filename)