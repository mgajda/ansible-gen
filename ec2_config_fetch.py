#!/bin/python

#
# get ec2 instance config from aws and save in ec2_config.yml
# which use ansible playbook for provisioning similar instances
#

import boto3 
import yaml
import getopt, sys


def usage():
  	print '\nUsage: '+sys.argv[0]+' -i <file1> [option]'

def get_config(name):
	my_session = boto3.session.Session()
	my_region = my_session.region_name
	ec2 = boto3.client('ec2')  
	filters = [{  
    		'Name': 'tag:Name',
    		'Values': [name]
    	}]
	response = ec2.describe_instances(Filters=filters)  
	#response = ec2.describe_instances()  
	for r in response['Reservations']:
  		for i in r['Instances']:
    			config = {'instance_type':i['InstanceType'], \
			'security_group': i['SecurityGroups'][0]['GroupId'], \
			'image':i['ImageId'], 'region':my_region, 'keypair':i['KeyName']}
    			with open('ec2_config.yaml', 'w') as f:
				print "Creating config file for instance "+name
     				yaml.dump(config, f, default_flow_style=False)

def main(argv):
	try:
    		opts, args = getopt.getopt(argv, 'hi:o:tbpms:', ['help', 'name='])
    		if not opts:
      			print 'No options supplied'
      			usage()
  	except getopt.GetoptError,e:
    		print e
    		usage()
    		sys.exit(2)
  	name=None
  	for opt, arg in opts:
    		if opt in ('-h', '--help'):
      			usage()
      			sys.exit(2)
    		elif opt in ("-n", "--name"):
      			name = arg
      			get_config(name)


if __name__ =='__main__':
    main(sys.argv[1:])
