#!/usr/bin/python
"""
Build script of creating docker-compose.yml
Extract info running containers, and 
generates compose yaml (services against each containers)
Note: link containers not supported yet!
"""

import yaml
import docker
import subprocess
import json
from aws_ecr import *
from terraform_create import *

def build_from_running_containers(ids=None, account_id=None, build_image=False):
	client = docker.from_env()
	if ids==None:
		containers = client.containers.list()
	else:
		# containers from given ids
		containers = client.containers.list(filters={'status': 'running', 'id': ids})
	template = {'services': {}, 'version': '3'}
	for c in containers:
		service = {}
	
		# image info
		image = c.attrs['Config']['Image']
		#tag = c.attrs['Config']['Labels']
	
		# correction	
		service['image'] = str(image)
		#if tag:
		#	service['image'] = (str(image) + ":" + str(tag))
		#else:
		#	service['image'] = (str(image))

		# mount volume info
		# TODO: multiple mounts
		if len(c.attrs['Mounts']):
			dest_volume = c.attrs['Mounts'][0]['Destination']
			source_volume = c.attrs['Mounts'][0]['Source']
			service['volumes'] = [str(source_volume) + ":" + str(dest_volume)]

		# port mapping info ( handle tcp port only yet)
		# default port will be zero, if some container working as client, 
		# and didn't host any service, then we didn't need port 
		innerport = '0' 	
		urls = c.attrs['NetworkSettings']['Ports']
		for url in urls:
			innerport = url.split('/')[0]
			if urls[url]:   # TCP ports
				outerport = urls[url][0]['HostPort']
				service['ports'] = [str(innerport)+':'+str(outerport)]

		# service name info
		# default service name is same as image name, if netstat is not present in container
		service_name = str(image)
		pid=c.attrs['State']['Pid']
		netstat_command=['pkexec', 'nsenter', '-t', str(pid), '-n', 'netstat', '-tulpn']
		netstat_output=subprocess.check_output(netstat_command)
		for row in netstat_output.split(b'\n'):
			if str.encode(innerport) in row:
				if row.split()[0] == b'tcp':
					service_name = row.split()[6].split('/')[1]

		# append service
		template['services'][service_name] = service

		# if aws account id is defined
		# 	build image with same tag as container and push to ECR
		#       create task defination with port mapping and mount volume in terraform dir
		#       create service.tf in terraform dir with app name
		image_name = image.split(':')[0]	
		tag = image.split(':')[1]
		build_and_ecr_push(tag, account_id, image_name, build_image)
		create_task_definition(service_name, account_id, service)	

	#print yaml.dump(template, default_flow_style=False)
	with open('docker-compose.yml', 'w') as outfile:
		yaml.dump(template, outfile, default_flow_style=False)

