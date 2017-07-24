#!/usr/bin/python
import yaml
from collections import OrderedDict

# Local variables
BASH_HISTORY='bash_history'
REMOTE_USER='ubuntu'
HOST='ec2'
HOME_DIRECTORY='/home/ubuntu'

# Just define it for maintain order in yml
class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass

class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))

yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)

# Start creating first play in yml
header=[UnsortableOrderedDict({'name': 'Bash converted playbook', \
	'hosts': HOST,'sudo':'yes', 'remote_user': REMOTE_USER, 'environment': {'PWD':'/home/ubuntu'}})]
header[0]['tasks'] = [{'name':'change directory','set_fact':{'cwd': HOME_DIRECTORY}}]  # Initially set current working directory as home directory

# Read the bash history file
with open(BASH_HISTORY,'r') as f:
	for line in f:
		if not line.strip():
			print("We got empty line.")
		else:
			cmd_arr=line.split()
			if cmd_arr[0] is '#':
				print("Comment line. Ignoring")

			# Start handling following commands
			elif 'apt-get' in cmd_arr:
				if 'install' in cmd_arr:
					if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
					if '-y' in cmd_arr: cmd_arr.remove('-y')
					if 'apt-get' in cmd_arr: cmd_arr.remove('apt-get')
					if 'install' in cmd_arr: cmd_arr.remove('install')
					for package in cmd_arr: # Here we have list of packages to be install
						new_task=UnsortableOrderedDict({'name':'Install package','apt':{'name':package,'state':'present'}})
						header[0]['tasks'].append(new_task)
				elif 'update;' in cmd_arr:
					new_task=UnsortableOrderedDict({'name':'Run apt-get update','apt':{'update_cache':'yes'}})
					header[0]['tasks'].append(new_task)
				elif 'dist-upgrade' in cmd_arr:
					new_task=UnsortableOrderedDict({'name':'Run apt-get dist-upgrade','apt':{'upgrade':'dist'}})
					header[0]['tasks'].append(new_task)
				else:
					print("apt-get argument not supported")

			elif 'pip' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				if '-r' in cmd_arr:
					cmd_arr.remove('-r')
					new_task=UnsortableOrderedDict({'name':'pip packages','pip': {'requirements': '{{ cwd }}/requirment.txt'}})
					header[0]['tasks'].append(new_task)
				#elif (pakcages list in argument -> case need to implement )

			elif 'export' in cmd_arr:
				# need to handle enviroment vairable, either using ansible environment or using ~/.bashrc
				# currently thinking on it
				print(cmd_arr[1])

			elif 'echo' in cmd_arr:
				echo_line=" ".join(cmd_arr)
				new_task=UnsortableOrderedDict({'name':'echo','shell': echo_line })
				header[0]['tasks'].append(new_task)

			elif 'cd' in cmd_arr: # I am using fact variable to keep track of current working directory
				new_task=UnsortableOrderedDict({'name':'change directory','set_fact':{'cwd': cmd_arr[1]}})	
				header[0]['tasks'].append(new_task)

			elif 'chown' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				if '-R' in cmd_arr: cmd_arr.remove('-R')
				user=cmd_arr[1].split(':')[0]
				group=cmd_arr[1].split(':')[1]
				new_task=UnsortableOrderedDict({'name':'chown directory', \
					'file':{'dest':cmd_arr[2],'owner':user,'group':group,'recurse':'yes'}})
				header[0]['tasks'].append(new_task)

			elif 'mkdir' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				if 'mkdir' in cmd_arr: cmd_arr.remove('mkdir')
				if '-p' in cmd_arr: cmd_arr.remove('-p') # May be we have -p option
				for item in cmd_arr: # Here we have list of directories to be created
					new_task=UnsortableOrderedDict({'name':'Create directory','file': {'path': item, 'state':'directory'}})
					header[0]['tasks'].append(new_task)
					# currently only handle absolute path, will create case of relative path if needed
 
			elif 'mount' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				new_task=UnsortableOrderedDict({'name':'Mount directory', 'mount': {'path': cmd_arr[1]}})
				header[0]['tasks'].append(new_task)

			elif 'git' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				git_line=" ".join(cmd_arr)
				new_task=UnsortableOrderedDict({'name':'Git clone', 'shell': 'cd {{ cwd }} && '+ git_line})
				header[0]['tasks'].append(new_task)

			elif 'rm' in cmd_arr:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				if 'rm' in cmd_arr: cmd_arr.remove('rm')
				if '-rf' in cmd_arr: cmd_arr.remove('-rf')
				for item in cmd_arr: # Here we have list of directories to be deleted
					new_task=UnsortableOrderedDict({'name':'rm dir','file': {'state':'absent', 'path': "{{ cwd }}/" +item+"" }})
					header[0]['tasks'].append(new_task)
					# currently only handle relative path, will create case of absolute path if needed 
			else:
				print("Command not implemented or not found")
			
			
# Generate yml file read by ansible				
with open('ansible.yml', 'w') as outfile:
    yaml.dump(header, outfile, default_flow_style=False, explicit_start=True, allow_unicode=True)
