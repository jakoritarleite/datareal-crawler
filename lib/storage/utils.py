import boto3
import hashlib
from datetime import datetime

from lib.url import extract_domain, extract_path

def get_imagename_from_url(url: str) -> str:
    """Returns the image filename using md5

    Args:
        param1 (str) url:
            The url we will get the name of

    Returns a string which is the filename (md5(url.path))
    """
    return hashlib.md5(url.encode()).hexdigest()

def get_filename_from_url(url: str) -> {str: str}:
    """Returns a dict containing the filename and folder using md5

    Args:
        param1 (str) url:
            The url to get the name and folder of

    Returns a dict containing the folder (md5 -> url.domain) and the filename (md5 -> url.path)
    """
    domain = extract_domain(url=url)
    path = extract_path(url=url)

    folder = hashlib.md5(domain.encode()).hexdigest()
    file = hashlib.md5(path.encode()).hexdigest()

    response = {
        'folder': f"{folder}/{file}",
        'file': datetime.today().strftime("%Y-%m-%d") + '.body'
    }

    return response

def upload(bucket: str, filename: str, content: bytes):
    print(f"uploading {filename} to {bucket}")
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(content, bucket, filename)
    except Exception as error:
        print('got error uploading file to S3', error)