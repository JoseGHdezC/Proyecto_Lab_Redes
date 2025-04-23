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

### NetworkAutomation
1. Añadir a la configuración de NetworkAutomation:
```
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
1. Incluir ficheros .yml en /ansible_data
2. Crear clave ssh
``` bash
$ ssh-keygen -t rsa -n 2048
$ ssh-copy-id manager@192.168.1.2
```