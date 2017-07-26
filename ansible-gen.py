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
#header=[UnsortableOrderedDict({'name': 'Bash converted playbook', \
#	'hosts': HOST,'remote_user': REMOTE_USER, 'environment': {'PWD':'/home/ubuntu'}})]
header=[UnsortableOrderedDict([ ('name', 'Bash converted playbook'), \
	('hosts', HOST), ('remote_user', REMOTE_USER), ('environment', {'PWD':'/home/ubuntu'}) ])]
header[0]['tasks'] = [{'name':'Set default working directory','set_fact':{'cwd': HOME_DIRECTORY}}]  # Initially set current working directory as home directory

# Read the bash history file
i=0
with open(BASH_HISTORY,'r') as f:
	for line in f:
		i += 1
		if not line.strip():
			print("We got empty line.")
		else:
			cmd_arr=line.split()
			sudo='no'
			if cmd_arr[0] is '#':
				print("Comment line. Ignoring")

			# Start handling following commands
			elif 'apt-get' in cmd_arr:
				if 'install' in cmd_arr:
					command_line=" ".join(cmd_arr)
					if 'sudo' in cmd_arr: 
						cmd_arr.remove('sudo')
						sudo='yes'
					if '-y' in cmd_arr: cmd_arr.remove('-y')
					if 'apt-get' in cmd_arr: cmd_arr.remove('apt-get')
					if 'install' in cmd_arr: cmd_arr.remove('install')
					#new_task=UnsortableOrderedDict({'name':command_line, 'sudo':sudo, \
					#		'apt':{'name':'{{ item }}','state':'present'}})
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), \
							('apt',{'name':'{{ item }}','state':'present'}) ])
					packages = []
					for package in cmd_arr: # Here we have list of packages to be install
						packages.append(package)
					new_task['with_items'] = packages
					header[0]['tasks'].append(new_task)
				elif 'update;' in cmd_arr:
					command_line=" ".join(cmd_arr)
					if 'sudo' in cmd_arr: 
						cmd_arr.remove('sudo')
						sudo='yes'
					#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo,'apt':{'update_cache':'yes'}})
					new_task=UnsortableOrderedDict([ ('name', command_line), ('sudo',sudo) ,('apt',{'update_cache':'yes'}) ])
					header[0]['tasks'].append(new_task)
				elif 'dist-upgrade' in cmd_arr:
					command_line=" ".join(cmd_arr)
					if 'sudo' in cmd_arr: 
						cmd_arr.remove('sudo')
						sudo='yes'
					#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo,'apt':{'upgrade':'dist'}})
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), ('apt',{'upgrade':'dist'}) ])
					header[0]['tasks'].append(new_task)
				else:
					print("apt-get argument not supported")

			elif 'pip' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if '-r' in cmd_arr:
					cmd_arr.remove('-r')
					#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo,'pip': {'requirements': '{{ cwd }}/requirment.txt'}})
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), ('pip', {'requirements': '{{ cwd }}/requirment.txt'}) ])
					header[0]['tasks'].append(new_task)
				#elif (pakcages list in argument -> case need to implement )

			elif 'export' in cmd_arr:
				# need to handle enviroment vairable, either using ansible environment or using ~/.bashrc
				# currently thinking on it
				print(cmd_arr[1])

			elif 'echo' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				echo_line=" ".join(cmd_arr)
				#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo,'shell': echo_line })
				new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), ('shell', echo_line) ])
				header[0]['tasks'].append(new_task)

			elif 'cd' in cmd_arr: # I am using fact variable to keep track of current working directory
				command_line=" ".join(cmd_arr)
				#new_task=UnsortableOrderedDict({'name':command_line,'set_fact':{'cwd': cmd_arr[1]}})	
				new_task=UnsortableOrderedDict([ ('name',command_line),('set_fact',{'cwd': cmd_arr[1]}) ])	
				header[0]['tasks'].append(new_task)

			elif 'chown' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if '-R' in cmd_arr: cmd_arr.remove('-R')
				user=cmd_arr[1].split(':')[0]
				group=cmd_arr[1].split(':')[1]
				#new_task=UnsortableOrderedDict({'name':command_line, 'sudo': sudo, \
				#	'file':{'dest':cmd_arr[2],'owner':user,'group':group,'recurse':'yes'}})
				new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo', sudo), \
					('file',{'dest':cmd_arr[2],'owner':user,'group':group,'recurse':'yes'}) ])
				header[0]['tasks'].append(new_task)

			elif 'mkdir' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if 'mkdir' in cmd_arr: cmd_arr.remove('mkdir')
				if '-p' in cmd_arr: cmd_arr.remove('-p') # May be we have -p option
				for item in cmd_arr: # Here we have list of directories to be created
					#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo, \
					#	'file': {'path': item, 'state':'directory'}})
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), \
						('file', {'path': item, 'state':'directory'}) ])
					header[0]['tasks'].append(new_task)
					# currently only handle absolute path, will create case of relative path if needed
 
			elif 'mount' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				new_task=UnsortableOrderedDict([('name',command_line), ('sudo',sudo), ('mount', {'path': cmd_arr[1]})])
				#new_task=UnsortableOrderedDict({'name':command_line, 'sudo':sudo, 'mount': {'path': cmd_arr[1]}})
				header[0]['tasks'].append(new_task)

			elif 'git' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				git_line=" ".join(cmd_arr)
				#new_task=UnsortableOrderedDict({'name':command_line,'sudo':sudo, 'shell': 'cd {{ cwd }} && '+ git_line})
				new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('shell', 'cd {{ cwd }} && '+ git_line) ])
				header[0]['tasks'].append(new_task)

			elif 'rm' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if 'rm' in cmd_arr: cmd_arr.remove('rm')
				if '-rf' in cmd_arr: cmd_arr.remove('-rf')
				#new_task=UnsortableOrderedDict({'name':command_line, 'sudo':sudo, \
				#			'file':{'path':'{{ item }}','state':'absent'}})
				new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), \
							('file',{'path':'{{ item }}','state':'absent'}) ])
				dirs = []
				for item in cmd_arr: # Here we have list of directories to be deleted
					dirs.append("{{ cwd }}/"+ item)
				new_task['with_items'] = dirs
				header[0]['tasks'].append(new_task)
					# currently only handle relative path, will create case of absolute path if needed 
			else:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				print("Command "+ cmd_arr[0]+" not implemented or not found. Line no " + str(i))
			
			
# Generate yml file read by ansible				
with open('ansible.yml', 'w') as outfile:
    yaml.dump(header, outfile, default_flow_style=False, explicit_start=True, allow_unicode=True)
