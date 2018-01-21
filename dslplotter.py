#!/usr/bin/python
from lxml import html
import requests
import re
import json
import urllib2
import config
import boto3
import time

while True:
	dynamodb = boto3.resource('dynamodb', aws_access_key_id=config.aws_access_key_id, aws_secret_access_key=config.aws_secret_access_key, region_name=config.region_name)
	table = dynamodb.Table('dslplotter')

	if config.use_url:
		router_page = requests.get(config.router_url)
		content = router_page.content
		tree = html.fromstring(content)
	else:
		file=open(config.router_file, 'r');
		content = file.read()
		tree = html.fromstring(content)
		file.close()

	weather = json.loads(requests.get(config.weather_url).content)

	data = {}
	data['AttenuationAt300k'] = tree.xpath('//*[@id="contents"]/table[5]/tr[11]/td[2]/text()')[0]
	data['ExcessiveImpulseNoise'] = tree.xpath('//*[@id="contents"]/table[5]/tr[14]/td[2]/text()')[0]
	data['DnNoiseMargin'] = tree.xpath('//*[@id="contents"]/table[5]/tr[4]/td[2]/text()')[0]
	data['UpNoiseMargin'] = tree.xpath('//*[@id="contents"]/table[5]/tr[4]/td[3]/text()')[0]
	data['UpAttenuation'] = tree.xpath('//*[@id="contents"]/table[5]/tr[5]/td[3]/text()')[0]
	data['DnAttenuation'] = tree.xpath('//*[@id="contents"]/table[5]/tr[5]/td[2]/text()')[0]

	data['E15Retrains'] = 				tree.xpath('//*[@id="contents"]/table[7]/tr[2]/td[4]/text()')[0]
	data['E15DSLTrainingErrors'] = 		tree.xpath('//*[@id="contents"]/table[7]/tr[3]/td[4]/text()')[0]
	data['E15TrainingTimeouts'] = 		tree.xpath('//*[@id="contents"]/table[7]/tr[4]/td[4]/text()')[0]
	data['E15LossofFraming'] = 			tree.xpath('//*[@id="contents"]/table[7]/tr[5]/td[4]/text()')[0]
	data['E15LossofSignal'] = 			tree.xpath('//*[@id="contents"]/table[7]/tr[6]/td[4]/text()')[0]
	data['E15LossofPower'] = 			tree.xpath('//*[@id="contents"]/table[7]/tr[7]/td[4]/text()')[0]
	data['E15LossofMargin'] = 			tree.xpath('//*[@id="contents"]/table[7]/tr[8]/td[4]/text()')[0]
	data['E15SecsWErr'] = 				tree.xpath('//*[@id="contents"]/table[7]/tr[9]/td[4]/text()')[0]
	data['E15SecsSevereErr'] = 			tree.xpath('//*[@id="contents"]/table[7]/tr[10]/td[4]/text()')[0]
	data['E15CorrectedBlocks'] = 		tree.xpath('//*[@id="contents"]/table[7]/tr[11]/td[4]/text()')[0]
	data['E15UncorrectableBlocks'] = 	tree.xpath('//*[@id="contents"]/table[7]/tr[12]/td[4]/text()')[0]
	data['E15DSLUnavailSecs'] = 		tree.xpath('//*[@id="contents"]/table[7]/tr[13]/td[4]/text()')[0]
	data['Precip_1hr_in'] = 			weather['current_observation']['precip_1hr_in']
	data['timestamp'] = int(time.time())

	r = re.compile('[0-9\.-]+')
	for k,v in data.items():
		try:
			data[k] = r.match(v).group(0)
		except Exception as e:
			print(e)

	table.put_item(Item=data)

	time.sleep(config.sleep_time)