# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT

sudo apt update
# sudo apt-get -y upgrade

sudo apt-get -y install python-dev python-pip
sudo pip install -U virtualenv
pip install --user --upgrade tensorflow==1.12

sudo apt-get -y install python3-dev python3-pip
sudo pip3 install -U virtualenv                     # system-wide install
pip3 install --user --upgrade tensorflow==1.12      # CPU

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
