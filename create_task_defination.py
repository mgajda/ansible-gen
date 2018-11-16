import json

data = {}  
data['name'] = 'app'
data['image'] = 'XXXXXXXXXXX.dkr.ecr.eu-west-1.amazonaws.com/app'
data['cpu'] = 10
data['memory'] = 512
data['portMappings'] = []  
data['portMappings'].append({  
    'containerPort': 8000,
    'hostPort': 8000,
    'protocol': 'tcp'
})
data['essential'] = True
data['mountPoints'] = []  
data['volumesFrom'] = []  

with open('app.json', 'w') as outfile:  
    json.dump(data, outfile,  indent=4)
