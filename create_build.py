#!/usr/bin/python
"""
Main program for calling build generator
Automate build using bash history and running containers
"""
import optparse

#custom imports
from build_bash_history import build_from_bash_history
from build_running_containers import build_from_running_containers 

def docker_args_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))

def main():
	parser = optparse.OptionParser()
	
	parser.add_option('-i', '--input',
                  action="store",
                  dest="input_bash",
                  default="bash_history",
                  help="bash_history file path, default is bash_history in current directory")

	parser.add_option('-b', '--base-image',
                  action="store",
                  dest="base_image",
                  default="ubuntu:16.04",
                  help="base image name, default is ubuntu:14.04")

	parser.add_option('--ansible', 
                  action="store_const",
                  const='ansible',
                  dest='build_type',
                  default='ansible',
                  help="Create ansible yml")

	parser.add_option('--docker',
                  action='store_const',
                  const='docker',
                  dest='build_type',
                  help="Create Dockerfile")

	parser.add_option('--docker-id',
                  type='string',
                  action='callback',
                  callback=docker_args_callback,
		  dest = 'docker_args_list')

	parser.add_option('-a', '--aws-id',
                  action="store",
                  dest="aws_account_id",
                  help="aws account id, where cluster need to create and docker registry")

	parser.add_option('--rebuild',
                  action="store_true",
                  default=False,
                  dest="rebuild_enable",
                  help="rebuid the given docker image from source")

	options, args = parser.parse_args()

	btype = options.build_type
	iname = options.input_bash
	bimage = options.base_image
	container_list = options.docker_args_list
	aws_account_id = options.aws_account_id
	build_image = options.rebuild_enable
	
	build_from_bash_history(btype, iname, bimage)

	if btype == 'docker':
		build_from_running_containers(container_list, aws_account_id, build_image)

	# future steps..


if __name__ == '__main__':
	main()
