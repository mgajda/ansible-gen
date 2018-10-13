#!/usr/bin/python
"""
Main program for calling build generator
Automate build using bash history and running containers
"""
import optparse

#custom imports
from build_bash_history import build_from_bash_history
from build_running_containers import build_from_running_containers 

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
                  default="ubuntu:14.04",
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


	options, args = parser.parse_args()

	btype = options.build_type
	iname = options.input_bash
	bimage = options.base_image

	
	build_from_bash_history(btype, iname, bimage)
	if btype == 'docker':
		build_from_running_containers()

	# future steps..


if __name__ == '__main__':
	main()
