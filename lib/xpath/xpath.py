from __future__ import annotations

from boto3 import resource
from boto3.dynamodb import conditions

from lib.url import extract_domain

dynamodb = resource('dynamodb')

def get_xpaths(table: str, url: str) -> Dict[str, str]:
    """Docstring for the get_xpath function.

    Query DynamoDB using the domain for the
    XPath configuration on the given Table ``table``.

    Args:
        param1 (str) table:
            The DynamoDB table name to get the XPath obj from
        param2 (str) url:
            The url that will be extracted from the domain to make the query

    Returns:
        Object containing the XPath configurations from DynamoDB
    """
    _table = dynamodb.Table(table)
    domain: str = extract_domain(url)

    response = _table.query(
        IndexName='domain-index',
        KeyConditionExpression=conditions.Key('domain').eq(domain)
    )

    return response['Items'][0]