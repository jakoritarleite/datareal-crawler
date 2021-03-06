from __future__ import annotations

from io import BytesIO
from os.path import split
from base64 import b64decode
from urllib.parse import urlparse

from lib.request import librequest
from lib.fake_headers import UserAgent

def get_from_url(url: str, do_render: bool = False) -> bytes:
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
        response = librequest.request(
            url=url,
            method='GET',
            render=do_render,
            user_agent=f"User-Agent: {UserAgent().random()}",
            use_proxy=False)

        content = response['content']
        print(f'response from request {response["status_code"]}')
        print(f'html content len<{len(content)}>')

        if response['status_code'] != 200:
            print('Status code was not 200, trying to handle it using Proxy.')
            response = librequest.request(
                url=url,
                method='GET',
                render=do_render,
                user_agent=f"User-Agent: {UserAgent().random()}",
                use_proxy=True)

            content = response['content']

    elif url == None:
        raise Exception('URL Must not be None.\nNote that if the Spider crawled every page, it will return None at the end.')

    return response['status_code'], content

def get_from_body(html_content: bytes) -> bytes:
    content: bytes

    try:
        content = BytesIO()
        content.write(html_content.encode())

    except Exception:
        raise Exception('Failed when streaming the HTML content')

    return b64decode(content.getvalue())