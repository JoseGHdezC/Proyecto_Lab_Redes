# Proyecto Laboratorio de Redes: Creación de topología spine-leaf
## Preparación
1. Creación del entorno virtual
```py
python3 -m venv gns3fy_virtual
source ./gns3fy_virtual/bin/activate
```
2. Instalar dependencias
```python
pip install -r requirements.txt
```

## Configuración de Ansible
En primer lugar tenemos que obtener los templates de NetworkAutomation y FRR8.2.2

### FRR 8.2.2
1. Cambiar en la pestaña Network del template el número de puertos
2. Añadir usuario manager al dispositivo
   1. `adduser manager`
3. Asignar ip de gestión
   1. Volátil: 
   ``` bash
   #> ip addr add {ip}/{netmask} dev {interface}
   #> ip link set {interface} up
   ```

### NetworkAutomation
1. Añadir a la configuración de NetworkAutomation:
``` bash
auto eth0
iface eth0 inet static
	address 192.168.1.1
	netmask 255.255.255.0
```
1. Entrar en 'Configure' de NetworkAutomation y añadir /ansible_data en directorios adicionales
2. En NetworkAutomation ejecutar (usar 1000:1000 o el respectivo de tu usuario, por lo general será ese):
``` bash
$ chown -R 1000:1000 /ansible_data
```
3. Incluir ficheros .yml en /ansible_data
4. Crear clave ssh
``` bash
$ ssh-keygen -t rsa -n 2048
$ ssh-copy-id manager@192.168.1.2
```
5. Ejecutar archivos de configuración para configurar la red de gestión
``` bash
$ ansible-playbook -i hosts.yml management_ip_spine.yaml --ask-become-pass
$ ansible-playbook -i hosts.yml management_ip_leaf.yaml --ask-become-pass
```
6. Ejecutar archivos de configuración para configurar nodos spine
``` bash
$ ansible-playbook -i hosts.yml spine_conf.yaml --ask-become-pass
```
7. Ejecutar archivos de configuración para configurar nodos leaf
``` bash
$ ansible-playbook -i hosts.yml leaf_conf.yaml --ask-become-pass
```