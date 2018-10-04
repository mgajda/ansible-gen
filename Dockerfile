FROM ubuntu:14.04
COPY ansible/* .ssh/
ENV HISTFILESIZE=1000
ENV HISTSIZE=1000
RUN apt-get update;
RUN apt-get dist-upgrade -y;
RUN apt-get install -y python-pip chromium-browser chromium-chromedriver
RUN mkdir /media/scraped
# chown remain in effect on mounted volume 
# echo /dev/xvdp /media/scraped/ ext4 auto 0 1 >> /etc/fstab
VOLUME ["/media/scraped"]
# chown remain in effect on mounted volume 
RUN git clone git@github.com:mgajda/scraper-python.git
WORKDIR scraper-python
RUN pip install -r requirements.txt
RUN rm -rf html logs output_csv
