#!/usr/bin/python
"""
Build script of creating docker-compose.yml
Extract info running containers, and 
generates compose yaml (services against each containers)
Note: link containers not supported yet!
"""

import yaml
import docker

client = docker.from_env()
#container = client.containers.get('3860f5b3993b')
containers = client.containers.list()
template = {'services': {}, 'version': '3'}
for c in containers:
	service = {}

	# image info
	image = c.attrs['Config']['Image']
	tag = c.attrs['Config']['Labels']
	if tag:
		service['image'] = (str(image) + ":" + str(tag))
	else:
		service['image'] = (str(image))

	# mount volume info
	dest_volume = c.attrs['Mounts'][0]['Destination']
	source_volume = c.attrs['Mounts'][0]['Source']
	service['volumes'] = [str(source_volume) + ":" + str(dest_volume)]

	# port mapping info ( handle tcp port only yet)
	urls = c.attrs['NetworkSettings']['Ports']
	for url in urls:
		innerport = url.split('/')[0]
		if urls[url]:   # TCP ports
			outerport = urls[url][0]['HostPort']
			service['ports'] = [str(innerport)+':'+str(outerport)]

	# service name info
	netstat_output=c.exec_run("netstat -tulpn").output
	for row in netstat_output.split('\n'):
		if innerport in row:
			if row.split()[0] == 'tcp':
				service_name = row.split()[6].split('/')[1]

	# append service
	template['services'][service_name] = service

#print yaml.dump(template, default_flow_style=False)
with open('docker-compose.yml', 'w') as outfile:
	yaml.dump(template, outfile, default_flow_style=False)

