from __future__ import annotations

import boto3
import requests
import threading
import multiprocessing
import concurrent.futures

from time import time
from json import dumps
from os import environ

from lib.images import resize_image
from lib.database import scan_table
from lib.database import update_item
from lib.storage import upload
from lib.storage import get_filename_from_url
from lib.storage import get_imagename_from_url


def run(event, context):
	"""Docstring for download_image.run function

	Args:
		param1 (str|None) event:LastEvaluatedKey:
			The key to the next page of the Table

	It will iter throught all db items and request all images
	within this item (if the s3_url is not there), then will resize it
	and upload to a S3 bucket.
	"""
	lambda_client = boto3.client('lambda')
	response: dict = {'status': 200}
	start_key: str = event.get('LastEvaluatedKey')
	processes = list()
	# If you want to set a limit to the returned items, add {'Limit': X} inside the dict function below
	# This is usefull so the Lambda function don't time out
	query = dict({'Limit': 10})

	if start_key:
		query['ExclusiveStartKey'] = start_key

	items, last_key = scan_table(environ.get('PROPERTIES_TABLE_NAME'), query)

	print('items_len', len(items))
	print('last_key', last_key)

	for item in items:
		start_time = time()

		if not item['images']:
			continue

		process = multiprocessing.Process(target=process_items_images, args=(item,))
		processes.append(process)
		process.start()

	for process in processes:
		process.join()

	if last_key:
		lambda_client.invoke(
			FunctionName=environ.get('IMG_DOWNLOADER_ARN'),
			InvocationType='Event',
			Payload=dumps({'LastEvaluatedKey': last_key})
		)

		response.update({
			'LastEvaluatedKey': last_key
		})

	return response

def process_items_images(item: str):
	print(f"downloading and uploading images from {item['url']}")

	path = get_filename_from_url(item['url'])
	images_result = list()
	new_item = {
		'Key': {
			'id': item['id'],
			'url': item['url']
		},
		'AttributeName': 'images'
	}

	with concurrent.futures.ThreadPoolExecutor(max_workers=len(item['images'])) as executor:
		# This will create an executor just for the images that are not saved on S3
		future_to_image = { executor.submit(process_image, image['src']): image['src'] for image in item['images'] if not image.get('s3') }

		for future in concurrent.futures.as_completed(future_to_image):
			image = future_to_image[future]
			try:
				image_response = future.result()
			except Exception as exc:
				print(f"{image_response} generated an exception: {exc}")
			else:
				images_result.append(image_response)

	for image in item['images']:
		for _image in images_result:
			if _image['filename'] == get_imagename_from_url(image['src']):
				s3_path = f"{path['folder']}/{_image['filename']}.jpeg"
				upload('datareal-crawler-images', s3_path, _image['processed_image'])

				image.update({
					's3': 's3://datareal-crawler-images/' + s3_path
				})

	new_item.update({
		'Item': item['images']
	})

	update_item(environ.get('PROPERTIES_TABLE_NAME'), new_item)

def process_image(image_url: str) -> dict:
	response = requests.get(image_url, stream=True)

	if response.status_code == 200:
		processed_image = resize_image(response.content)
		filename = get_imagename_from_url(image_url)

		return {
			'filename': filename,
			'processed_image': processed_image
		}
	
	else:
		return {
			'error': response.status_code
		}