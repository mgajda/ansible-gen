#!/usr/bin/python
import yaml
from collections import OrderedDict
import re
import getopt, sys

# Local variables
BASH_HISTORY='bash_history'
REMOTE_USER='ubuntu'
HOST='ec2'
HOME_DIRECTORY='/home/ubuntu'

try:
	opts, args = getopt.getopt(sys.argv[1:], 'hi:o:tbpms:', ['help', 'input='])
    	if not opts:
      		print 'No options supplied'
  		print '\nUsage: '+sys.argv[0]+' -i <file1>'
    		sys.exit(2)
except getopt.GetoptError,e:
	print e
  	print '\nUsage: '+sys.argv[0]+' -i <file1>'
    	sys.exit(2)
name=None
for opt, arg in opts:
	if opt in ('-h', '--help'):
  		print '\nUsage: '+sys.argv[0]+' -i <file1>'
      		sys.exit(2)
    	elif opt in ("-i", "--input"):
      		name = arg

# Just define it for maintain order in yml
class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass

class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))

yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)

# Start creating first play in yml
# for testing with travis CI
header=[UnsortableOrderedDict([ ('name', 'Bash converted playbook'), ('connection', 'localhost'), \
	('hosts', 'localhost'), ('remote_user', REMOTE_USER), ('environment', {'PWD':'/home/ubuntu'}) ])]

# original header
#header=[UnsortableOrderedDict([ ('name', 'Bash converted playbook'), \
#	('hosts', HOST), ('remote_user', REMOTE_USER), ('environment', {'PWD':'/home/ubuntu'}) ])]

# Initially set current working directory as home directory
header[0]['tasks'] = [{'name':'Set default working directory','set_fact':{'cwd': HOME_DIRECTORY}}]

# Read the bash history file
i=0
with open(name,'r') as f:
	for line in f:
		i += 1
		if not line.strip():
			print("We got empty line.")
		else:
			line_without_comment=line.split('#',1)[0]
			cmd_arr=line_without_comment.split()
			sudo='no'
			if not cmd_arr:
				print("Comment line. Ignoring")

			# Start handling following commands
			#if 'apt-get' in cmd_arr:
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
				new_task=UnsortableOrderedDict([ ('name',command_line),('set_fact',{'cwd': '{{ cwd }}/'+cmd_arr[1]}) ])	
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
			elif 'docker' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if 'build' in cmd_arr:
					dockerfile=None
					durl=None
					dname=None
					dtag=None 
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
					new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('docker_image', {'dockerfile': dockerfile, 'name': dname, 'tag': dtag, 'path': '{{ cwd }}'}) ])
					header[0]['tasks'].append(new_task)
				if 'run' in cmd_arr:
					ports=None; inner=None; outer=None
					if 'docker' in cmd_arr: cmd_arr.remove('docker')
					if 'run' in cmd_arr: cmd_arr.remove('run')
					it = iter(cmd_arr)
					for opt in it:
						if opt == '-p':
							ports = next(it)
							print ports
							inner=ports.split(":")[0]
							outer=ports.split(":")[1]
						elif opt == '-v':
							volumes = next(it)
						else:
							image = opt
					new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('docker', {'image': image, 'state': 'started', 'ports': ([ports]) }) ])
					header[0]['tasks'].append(new_task)
					
			elif 'npm' in cmd_arr:
				command_line=" ".join(cmd_arr)
				global_flag='no'
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				cmd_arr.remove('npm')
				cmd_arr.remove('install')
				if not cmd_arr: # Must be package.json
					new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('npm', {'path': '{{ cwd }}' })])
				else:	
					if '-g' in cmd_arr:
						cmd_arr.remove('-g')
						global_flag='yes'
					new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('npm', {'name': cmd_arr[0], 'global': global_flag }) ])
				header[0]['tasks'].append(new_task)

			elif 'bower' in cmd_arr:
				command_line=" ".join(cmd_arr)
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				new_task=UnsortableOrderedDict([ ('name',command_line),('sudo',sudo), ('bower', {'path': '{{ cwd }}' })])
				header[0]['tasks'].append(new_task)
			
			elif 'scp' in cmd_arr:
				command_line=" ".join(cmd_arr)
				dir_flag=None
				wildcard="no"
				if 'sudo' in cmd_arr: 
					cmd_arr.remove('sudo')
					sudo='yes'
				if '-r' in cmd_arr:
					cmd_arr.remove('-r')
				if '*' in cmd_arr[1]:
					wildcard='yes'
					cmd_arr[1] = re.sub('[*]', '', cmd_arr[1])
				dst_path=cmd_arr[2].split(":")[1]
				print dst_path
				if dst_path is "":
					print dst_path
					dst='{{ cwd }}'
				elif dst_path[0] is '/':
					# absolute path
					dst=dst_path
				else:
					# relative path
					dst='{{ cwd }}/'+dst_path
				if wildcard == 'no':
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), \
							('copy',{'src': cmd_arr[1] \
							,'dest': dst }) ]) 
					header[0]['tasks'].append(new_task)
				else:
					src_loc=cmd_arr[1].rsplit('/',1)
					# wild card case
					new_task=UnsortableOrderedDict([ ('name',command_line), ('sudo',sudo), \
							#('local_action','shell ls '+cmd_arr[1]+'| awk -F "/" \'{print $NF}\''), \
							('local_action','shell ls '+cmd_arr[1]), \
							('register','key_file') ])
					header[0]['tasks'].append(new_task)
					new_task=UnsortableOrderedDict([ \
							('copy',{'src': ''+src_loc[0]+'/{{ item }}', \
							'dest': dst+'/{{ item }}' }), 
							('with_items',"{{ key_file.stdout_lines }}") ])
					header[0]['tasks'].append(new_task)
			else:
				if 'sudo' in cmd_arr: cmd_arr.remove('sudo')
				print("Command "+ cmd_arr[0]+" not implemented or not found. Line no " + str(i))
			
			
# Generate yml file read by ansible				
with open('ansible.yml', 'w') as outfile:
    yaml.dump(header, outfile, default_flow_style=False, explicit_start=True, allow_unicode=True)
