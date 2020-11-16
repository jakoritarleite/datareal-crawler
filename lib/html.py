from __future__ import annotations

from lib.models.request import Request

from io import BytesIO
from os.path import split
from base64 import b64decode
from urllib.parse import urlparse

def get_from_url(url: str) -> bytes:
    content: bytes

    if 's3' in url:
        parsed_url = urlparse(url)
        parsed_path = split(parsed_url.path)
        
        bucket = parsed_url.netloc
        path = parsed_path[0]
        filename = parsed_path[1]

        s3_object = S3Utils(
            bucket,
            path,
            filename
        )

        content = s3_object.download

    elif 'http' in url:
        request = Request(
            url,
            render=False
        )
        response = request.fetch()

        content = response.content

    else url == None:
        raise Exception('URL Must not be None.\nNote that if the Spider crawled every page, it will return None at the end.')

    return content 

def get_from_body(html_content: bytes) -> bytes:
    content: bytes
    
    try:
        content = BytesIO()
        content.write(html_content.encode())

    except Exception:
        raise Exception('Failed when streaming the HTML content')

    return b64decode(content.getvalue())