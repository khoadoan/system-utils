# application specific dirs
sudo mkdir -p /opt/verve
sudo chown -R hadoop:hadoop /opt/verve
sudo mkdir -p /var/verve/{data,lock,log/pig,tmp}
sudo chown -R hadoop:hadoop /var/verve

# install tmpreaper (apt for 2.x ami yum for 3.x ami)
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install tmpreaper || sudo yum install -y tmpreaper

# cron entries
