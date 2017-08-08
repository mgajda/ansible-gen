# LOCAL:
# Copy id_rsa, id_rsa.pub
scp ansible/* ie-scraper:.ssh/
ssh $TARGET -- << ENDSSH
# REMOTE:
chmod go-rwx .ssh/*
# Setup bash env
export HISTFILESIZE=1000
export HISTSIZE=1000
# With ROOT:
# Update all packages
sudo -s <<ENDROOT
sudo apt-get update;
sudo apt-get dist-upgrade -y;
sudo apt-get install -y python-pip chromium-browser chromium-chromedriver
# Mount EBS volume
mkdir /media/scraped
chown ubuntu:ubuntu /media/scraped
echo /dev/xvdp /media/scraped/ ext4 auto 0 1 >> /etc/fstab
mount /media/scraped
chown -R ubuntu:ubuntu /media/scraped
ENDROOT # ALL with ROOT
# Clone Git repo
git clone git@github.com:mgajda/scraper-python.git
cd scraper-python
# Install deps
pip install -r requirements.txt
rm -rf html logs output_csv
ln -s /media/scraped/* .
exit # check that exit or logout has been issued at the end (or warn)
ENDSSH

