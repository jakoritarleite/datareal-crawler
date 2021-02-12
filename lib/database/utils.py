from __future__ import annotations

import boto3
from botocore import exceptions

def scan_table(table: str, query: dict = dict()) -> Items:
    """Scan the designed table using kwargs
    
    Args:
        param1 (str) table: The DynamoDB Table name
        param2 (dict) query: The target query options

    Return:
        The response Items from DynamoDb which matches the query
        and the LastEvaluatedKey if exists
    """
    result = list()
    start_key = None

    boto3_client = boto3.resource('dynamodb')
    dynamo_client = boto3_client.Table(table)

    try:
        response = dynamo_client.scan(**query)
        result.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)

    except exceptions.ClientError as error:
        print(f'Error when scanning Dynamo {table}', error)

    else:
        return result, start_key

def update_item(table: str, query: dict = dict()) -> Response:
    if not query:
        raise Exception('Query param should not be empty.')

    boto3_client = boto3.resource('dynamodb')
    dynamo_client = boto3_client.Table(table)

    try:
        response = dynamo_client.update_item(
            Key=query['Key'],
            UpdateExpression=f"SET #atr=:atr",
            ExpressionAttributeValues={
                ':atr': query['Item']
            },
            ExpressionAttributeNames={
                '#atr': query['AttributeName']
            },
            ReturnValues='UPDATED_NEW'
        )

        return response

    except Exception as error:
        print('Error when updating item:', error)
        exit(1)