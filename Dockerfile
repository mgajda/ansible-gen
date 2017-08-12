FROM ubuntu:14.04
RUN apt-get update

# Install Ansible
RUN apt-get install -y software-properties-common git
RUN apt-add-repository -y ppa:ansible/ansible
RUN apt-get update
RUN apt-get install -y aptitude
RUN apt-get install -y ansible
