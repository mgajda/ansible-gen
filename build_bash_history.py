#!/usr/bin/python
"""
Build script generator using bash history
Support ansible and docker build
"""
from collections import OrderedDict
import re
import os
import yaml

# Local variables
#BASH_HISTORY='bash_history'
remote_user = 'ubuntu'
#HOST='ec2'
home_directory = '/home/ubuntu'


class UnsortableList(list):
	"""
	Just define it for maintain order in yml
	"""
	def sort(self, *args, **kwargs):
        	pass

class UnsortableOrderedDict(OrderedDict):
	"""
	Just define it for maintain order in yml
	"""
	def items(self, *args, **kwargs):
        	return UnsortableList(OrderedDict.items(self, *args, **kwargs))

def append_to_dockerfile(comment, command):
	"""Append command to Dockerfile"""
	with open("Dockerfile", "a") as docker:
		docker.write('#' + comment + '\n'  + command + '\n\n')

def build_from_bash_history(btype, iname, bimage):
	if btype == 'ansible':
		yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)

		# Start creating first play in yml
		# for testing with travis CI
		header = [UnsortableOrderedDict([('name', 'Bash converted playbook'), ('connection', 'localhost'), \
		('hosts', 'localhost'), ('remote_user', remote_user), ('environment', {'PWD':'/home/ubuntu'})])]

		# original header
		#header=[UnsortableOrderedDict([ ('name', 'Bash converted playbook'), \
		#	('hosts', HOST), ('remote_user', REMOTE_USER), ('environment', {'PWD':'/home/ubuntu'}) ])]

		# Initially set current working directory as home directory
		header[0]['tasks'] = [{'name':'Set default working directory', 'set_fact':{'cwd': home_directory}}]

	elif btype == 'docker':
		if os.path.exists('Dockerfile'):
    			os.remove('Dockerfile')
		# Adding base image
		cmd = 'FROM ' + bimage
		append_to_dockerfile('Base image', cmd)	

	else:
		print("Other build type Pending")

	# Read the bash history file
	line_num = 0
	with open(iname, 'r+') as f:
		lines = f.readlines()
		for i in range(0, len(lines)):
			line_num += 1
			line = lines[i]
			# This will ignore lines followed by # Error
 			if i+1 < len(lines):
				ne = lines[i + 1] 
				if (ne.startswith( '# Error' )):
					continue
			line_num += 1
			if not line.strip():
				print("We got empty line.")
			else:
				line_without_comment = line.split('#', 1)[0]
				cmd_arr = line_without_comment.split()
				sudo = 'no'
				if not cmd_arr:
					print("Comment line. Ignoring")
					continue

				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo = 'yes'
				ansible_skip = 0	
				# Start handling following commands
				if 'apt-get' in cmd_arr:
					if 'install' in cmd_arr:
						command_line = " ".join(cmd_arr)
						if '-y' in cmd_arr: cmd_arr.remove('-y')
						if 'apt-get' in cmd_arr: cmd_arr.remove('apt-get')
						if 'install' in cmd_arr: cmd_arr.remove('install')
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), \
							('apt', {'name':'{{ item }}', 'state':'present'})])
						packages = []
						for package in cmd_arr: # Here we have list of packages to be install
							packages.append(package)
						new_task['with_items'] = packages
					elif 'update;' in cmd_arr:
						command_line = " ".join(cmd_arr)
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('apt', {'update_cache':'yes'})])
					elif 'dist-upgrade' in cmd_arr:
						command_line = " ".join(cmd_arr)
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('apt', {'upgrade':'dist'})])
					else:
						print("apt-get argument not supported")
					# apt-get convert into RUN
					docker_cmd = 'RUN ' + " ".join(cmd_arr)
					docker_comments = 'Installing/Update packages'	
	
				elif 'pip' in cmd_arr:
					command_line = " ".join(cmd_arr)
					if '-r' in cmd_arr:
						cmd_arr.remove('-r')
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('pip', {'requirements': '{{ cwd }}/requirment.txt'})])
						#elif (pakcages list in argument -> case need to implement )
					# pip convert into RUN
					docker_cmd = 'RUN ' + " ".join(cmd_arr)
					docker_comments = 'Installing python packages'

				elif 'export' in cmd_arr:
					# need to handle enviroment vairable, either using ansible environment or using ~/.bashrc
					# currently thinking on it
					print(cmd_arr[1])
					# export convert into ENV
					docker_cmd = 'ENV ' + cmd_arr[1] 
					docker_comments = 'Setting env vars'

				elif 'echo' in cmd_arr:
					command_line = " ".join(cmd_arr)
					echo_line = " ".join(cmd_arr)
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('shell', echo_line)])
					docker_cmd = '# ' + " ".join(cmd_arr)
					docker_comments = ' '
					

				elif 'cd' in cmd_arr: # I am using fact variable to keep track of current working directory
					command_line = " ".join(cmd_arr)
					new_task = UnsortableOrderedDict([('name', command_line), ('set_fact', {'cwd': '{{ cwd }}/'+cmd_arr[1]})])	
					docker_cmd = 'WORKDIR ' + (cmd_arr[1])
					docker_comments = 'Change directory'

				elif 'chown' in cmd_arr:
					command_line = " ".join(cmd_arr)
					if '-R' in cmd_arr: cmd_arr.remove('-R')
					user = cmd_arr[1].split(':')[0]
					group = cmd_arr[1].split(':')[1]
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), \
					('file', {'dest':cmd_arr[2], 'owner':user, 'group':group, 'recurse':'yes'})])
					docker_cmd = '# chown remain in effect on mounted volume '
					docker_comments = 'Change ownership'

				elif 'mkdir' in cmd_arr:
					command_line = " ".join(cmd_arr)
					if 'mkdir' in cmd_arr: cmd_arr.remove('mkdir')
					if '-p' in cmd_arr: cmd_arr.remove('-p') # May be we have -p option
					ansible_skip = 1
					for item in cmd_arr: # Here we have list of directories to be created
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), \
						('file', {'path': item, 'state':'directory'})])
						header[0]['tasks'].append(new_task)
					docker_cmd = 'RUN ' + " ".join(cmd_arr)
					docker_comments = 'Creating directory'
 
				elif 'mount' in cmd_arr:
					command_line = " ".join(cmd_arr)
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('mount', {'path': cmd_arr[1]})])
					docker_cmd = 'VOLUME ["' + cmd_arr[1] + '"]'
					docker_comments = 'Mounting volume, will also handle in compose file'

				elif 'git' in cmd_arr:
					command_line = " ".join(cmd_arr)
					git_line = " ".join(cmd_arr)
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('shell', 'cd {{ cwd }} && '+ git_line)])
					docker_cmd = 'RUN ' + " ".join(cmd_arr)
					docker_comments = 'Git repo clone'

				elif 'rm' in cmd_arr:
					command_line = " ".join(cmd_arr)
					if 'rm' in cmd_arr: cmd_arr.remove('rm')
					if '-rf' in cmd_arr: cmd_arr.remove('-rf')
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), \
							('file', {'path':'{{ item }}', 'state':'absent'})])
					dirs = []
					for item in cmd_arr: # Here we have list of directories to be deleted
						dirs.append("{{ cwd }}/"+ item)
					new_task['with_items'] = dirs
					# currently only handle relative path, will create case of absolute path if needed

					docker_cmd = 'RUN ' + " ".join(cmd_arr)
					docker_comments = 'Removing dir'
	
				elif 'docker' in cmd_arr:
					command_line = " ".join(cmd_arr)
					if 'build' in cmd_arr:
						dockerfile = None
						durl = None
						dname = None
						dtag = None 
						if 'docker' in cmd_arr: cmd_arr.remove('docker')
						if 'build' in cmd_arr: cmd_arr.remove('build')
						it = iter(cmd_arr)
						for opt in it:
							if opt == '-f':
								dockerfile = next(it)
							elif opt == '-t':
								durl = next(it)
								dname = durl.split(":")[0]
								dtag = durl.split(":")[1]
							else:
								print opt
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('docker_image', {'dockerfile': dockerfile, 'name': dname, 'tag': dtag, 'path': '{{ cwd }}'})])
					if 'run' in cmd_arr:
						ports = None; inner = None; outer = None
						if 'docker' in cmd_arr: cmd_arr.remove('docker')
						if 'run' in cmd_arr: cmd_arr.remove('run')
						it = iter(cmd_arr)
						for opt in it:
							if opt == '-p':
								ports = next(it)
								print ports
								inner = ports.split(":")[0]
								outer = ports.split(":")[1]
							elif opt == '-v':
								volumes = next(it)
							else:
								image = opt
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('docker', {'image': image, 'state': 'started', 'ports': ([ports])})])

					docker_cmd = '# docker command not possible inside docker'
					docker_comments = 'docker execute'
					
				elif 'npm' in cmd_arr:
					command_line = " ".join(cmd_arr)
					global_flag = 'no'
					cmd_arr.remove('npm')
					cmd_arr.remove('install')
					if not cmd_arr: # Must be package.json
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('npm', {'path': '{{ cwd }}'})])
					else:	
						if '-g' in cmd_arr:
							cmd_arr.remove('-g')
							global_flag = 'yes'
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('npm', {'name': cmd_arr[0], 'global': global_flag})])

					docker_cmd = '# npm pending'
					docker_comments = 'npm operation'

				elif 'bower' in cmd_arr:
					command_line = " ".join(cmd_arr)
					new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), ('bower', {'path':'{{ cwd }}'})])
					docker_cmd = '# bower pending'
					docker_comments = 'bower execute'
			
				elif 'scp' in cmd_arr:
					ansible_skip = 1
					command_line = " ".join(cmd_arr)
					dir_flag = None
					wildcard = "no"
					if 'sudo' in cmd_arr: 
						cmd_arr.remove('sudo')
						sudo = 'yes'
					if '-r' in cmd_arr:
						cmd_arr.remove('-r')
					if '*' in cmd_arr[1]:
						wildcard = 'yes'
						cmd_arr[1] = re.sub('[*]', '', cmd_arr[1])
					dst_path = cmd_arr[2].split(":")[1]
					print dst_path
					if dst_path is "":
						print dst_path
						dst = '{{ cwd }}'
					elif dst_path[0] is '/':
						# absolute path
						dst = dst_path
					else:
						# relative path
						dst = '{{ cwd }}/'+dst_path
					if wildcard == 'no':
						new_task = UnsortableOrderedDict([('name', command_line), ('sudo', sudo), \
							('copy', {'src': cmd_arr[1] \
							, 'dest': dst})]) 
						header[0]['tasks'].append(new_task)
					else:
						src_loc = cmd_arr[1].rsplit('/', 1)
						# wild card case
						new_task = UnsortableOrderedDict([('name',command_line), ('sudo',sudo), \
						#('local_action','shell ls '+cmd_arr[1]+'| awk -F "/" \'{print $NF}\''), \
						('local_action', 'shell ls '+cmd_arr[1]), \
						('register', 'key_file')])
						header[0]['tasks'].append(new_task)
						new_task = UnsortableOrderedDict([ \
						('copy', {'src': ''+src_loc[0]+'/{{ item }}', \
						'dest': dst+'/{{ item }}'}), 
						('with_items', "{{ key_file.stdout_lines }}")])
						header[0]['tasks'].append(new_task)
					# scp convert into COPY
					docker_cmd = 'COPY ' + cmd_arr[1]  + ' ' + cmd_arr[2].split(":")[1]
					docker_comments = 'Copying files from host'
				else:
					print("Command "+ cmd_arr[0]+" not implemented or not found. Line no " + str(line_num))
					continue;
				
				if btype == 'ansible':
					if ansible_skip == 0:
						header[0]['tasks'].append(new_task)
				elif btype == 'docker':
					append_to_dockerfile(docker_comments, docker_cmd)
	
	# Generate yml file read by ansible
	if btype == 'ansible':
		with open('ansible.yml', 'w') as outfile:
    			yaml.dump(header, outfile, default_flow_style=False, explicit_start=True, allow_unicode=True)
