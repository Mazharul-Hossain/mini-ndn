# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT

sudo apt update
sudo apt-get -y upgrade

# sudo apt-get -y install python3-dev python3-pip
# pip3 install --upgrade pip3
# sudo pip3 install -U virtualenv  # system-wide install
# pip3 install --user --upgrade tensorflow==1.12      # CPU

sudo apt-get -y install python-dev python-pip
sudo pip install -U virtualenv
pip install --user --upgrade tensorflow==1.12

# https://stackoverflow.com/a/22674820/2049763
# Update the user's PYTHONPATH.
echo "export CPLUS_INCLUDE_PATH=\$CPLUS_INCLUDE_PATH:/usr/include/python2.7/" >> ~/.bashrc
# Also update root's PYTHONPATH in case of running under sudo.
echo "export CPLUS_INCLUDE_PATH=\$CPLUS_INCLUDE_PATH:/usr/include/python2.7/" | sudo tee -a /root/.bashrc > /dev/null

source ~/.bashrc
sudo source /root/.bashrc

ln -s /vagrant /home/vagrant/mini-ndn

# Check if install.sh is present or someone just copied the Vagrantfile directly
if [[ -f /home/vagrant/mini-ndn/install.sh ]]; then
  pushd /home/vagrant/mini-ndn
else
  # Remove the symlink
  rm /home/vagrant/mini-ndn
  git clone --depth 1 https://github.com/Mazharul-Hossain/mini-ndn.git
  pushd mini-ndn
fi
./install.sh -qa

SCRIPT

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", privileged: false, inline: $script
  config.vm.provider "virtualbox" do |vb|
    vb.name = "mini-ndn_box"
    vb.memory = 12288
    vb.cpus = 6
  end
end
