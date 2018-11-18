import json


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
