#Base image
FROM ubuntu:14.04

#Copying files from host
COPY ansible/* .ssh/

#Setting env vars
ENV HISTFILESIZE=1000

#Setting env vars
ENV HISTSIZE=1000

#Installing/Update packages
RUN apt-get update;

#Installing/Update packages
RUN apt-get dist-upgrade -y;

#Installing/Update packages
RUN apt-get install -y python-pip chromium-browser chromium-chromedriver

#Creating directory
RUN mkdir /media/scraped

#Change ownership
# chown remain in effect on mounted volume 

# 
# echo /dev/xvdp /media/scraped/ ext4 auto 0 1 >> /etc/fstab

#Mounting volume, will also handle in compose file
VOLUME ["/media/scraped"]

#Change ownership
# chown remain in effect on mounted volume 

#Git repo clone
RUN git clone git@github.com:mgajda/scraper-python.git

#Change directory
WORKDIR scraper-python

#Installing python packages
RUN pip install -r requirements.txt

#Removing dir
RUN rm -rf html logs output_csv

