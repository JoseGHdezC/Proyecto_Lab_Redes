# Laboratorio de Redes Project: Spine-leaf topology creation

## About the project
This project seeks to implement an automatic topology creator in the network simulator GNS3, using gns3fy API.  
When executing the program the user can specify the number of spine, leaf and server nodes which will be created and started.

## Preparation
To use the program locally, it is required to install the dependencies contained in the requirements.txt file.
1. Virtual environment creation
```py
python3 -m venv venv
source ./venv/bin/activate
```
2. Install dependencies
```python
pip install -r requirements.txt
```

## Ansible configuration
This project uses the following templates:

### FRR 8.2.2
1. Change number of ports for the template.
2. Add user manager to the device.
   1. `adduser manager`
3. Assign management ip.
   1. Configuration disappears when powering off the device: 
   ``` bash
   #> ip addr add {ip}/{netmask} dev {interface}
   #> ip link set {interface} up
   ```

### NetworkAutomation
1. Add to the configuration or to `/etc/network/interface`:
``` bash
auto eth0
iface eth0 inet static
	address 192.168.1.1
	netmask 255.255.255.0
```
2. Enter to 'Configure' and add '/ansible_data' in the additional directories block.
3. Execute command to change owner or privileges (use 1000:1000 (default) or the one assigned to your user):
``` bash
$ chown -R 1000:1000 /ansible_data
```
4. Include .yml and .yaml files in '/ansible_data'
5. Create ssh key
``` bash
$ ssh-keygen -t rsa -n 2048
$ ssh-copy-id manager@192.168.1.2
```
6. Execute configuration files to configure management network
``` bash
$ ansible-playbook -i hosts.yml management_ip_spine.yaml --ask-become-pass
$ ansible-playbook -i hosts.yml management_ip_leaf.yaml --ask-become-pass
$ ansible-playbook -i hosts.yml management_ip_server.yaml --ask-become-pass
```
7. Execute spine nodes configuration files
``` bash
$ ansible-playbook -i hosts.yml spine_conf.yaml --ask-become-pass
```
8. Execute leaf nodes configuration files
``` bash
$ ansible-playbook -i hosts.yml leaf_conf.yaml --ask-become-pass
```
9. Execute server nodes configuration files
``` bash
$ ansible-playbook -i hosts.yml server_conf.yaml --ask-become-pass
```

## Create Bridge in the leafs
When creating br0, assign as many interfaces as servers are going to connect.
```bash
ip link br0 type bridge
ip link set br0
ip link set eth3 master br0
ip link set eth3 up
```

### Doing a ping between virtual machines
``` bash
$ ip netns exec vm1 ping ip
```
> [!NOTE] This command will not work if the routing protocol for vxlan is BGP as the templates used in the project do not support the required command.