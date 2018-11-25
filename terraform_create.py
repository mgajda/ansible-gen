import json
from terrascript import Terrascript, variable


def create_task_definition(app_name, account_id, service):
	data = {}  
	data['name'] = app_name
	data['image'] = account_id + '.dkr.ecr.eu-west-1.amazonaws.com/' + app_name
	data['cpu'] = 10
	data['memory'] = 512
	data['portMappings'] = []
	if 'ports' in service:
		data['portMappings'].append({  
    			'containerPort': service['ports'][0].split(':')[0],
    			'hostPort': service['ports'][0].split(':')[1],
    			'protocol': 'tcp'
		})
	data['essential'] = True
	data['mountPoints'] = []  
	if 'volumes' in service:
		data['mountPoints'].append({  
    			'sourceVolume': service['volumes'][0].split(':')[0],
    			'containerPath': service['volumes'][0].split(':')[1]
		})
	data['volumesFrom'] = []  

	with open('app.json', 'w') as outfile:  
    		json.dump(data, outfile,  indent=4)

def create_variables(app_name, app_port, cluster_name):
	ts = Terrascript()

	var_access_key = variable('aws_access_key', default='')
	var_secret_key = variable('aws_secret_key', default='')
	var_region = variable('region', default='eu-west-1')
	var_ami = variable('ami', default='ami-066826c6a40879d75')
	var_az_qty = variable('az_qty', default='2')
	var_cluster_name = variable('ecs_cluster_name', default=cluster_name)
	var_instance_type = variable('instance_type', default='t2.micro')
	var_key_name = variable('key_name', default='rep')
	var_app_port = variable('app_port', default=app_port)
	var_app_name = variable('app_name', default=app_name)

	ts += var_access_key
	ts += var_secret_key
	ts += var_region
	ts += var_ami
	ts += var_az_qty
	ts += var_cluster_name
	ts += var_instance_type
	ts += var_key_name
	ts += var_app_port
	ts += var_app_name

	with open('variables.tf', 'w') as tfile:
		tfile.write(ts.dump())
