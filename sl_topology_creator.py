from gns3fy import Gns3Connector
from gns3fy import Project, Node
#import telnetlib3
import asyncio
from time import sleep

SERVER_TEMPLATE = "Network Automation"
ROUTER_TEMPLATE = "FRR 8.2.2"

"""
async def configure_router(host, port, interface, ip_address, subnet_mask) -> None:
    
    Conecta al router vía Telnet y configura la interfaz indicada.
    
    try:
        reader, writer = await telnetlib3.open_connection(host, port)

        await reader.readuntil("frr#")

        # Enviar comandos al router
        writer.write("exit\n")
        await writer.drain()
        writer.write(f"ip addr add {ip_address}/{subnet_mask} dev {interface}\n")
        await writer.drain()
        writer.write(f"ip link set {interface} up\n")
        await writer.drain()
        writer.write(f"adduser manager\n")
        await writer.drain()
        writer.write("manager\n")
        await writer.drain()
        writer.write("manager\n")
        await writer.drain()
            
        # Leer la respuesta para confirmar que se aplicó la configuración
        response = await reader.read(1024)
        print("Respuesta recibida:", response)
        
        # Close the connection when done
        writer.close()
        sleep(1)#
        
        print(f"Configuración aplicada a {interface}: {ip_address} {subnet_mask}")
    except Exception as e:
        print("Error durante la configuración:", e)
"""

def create_config_server(project, server) -> None:
    """
    Crea un nodo de configuración en el servidor Ansible.
    """
    server_name = "Servidor_Ansible"
    server_node = Node(project_id=project.project_id, name=server_name, template=SERVER_TEMPLATE,
                connector=server, x=0, y=0)
    server_node.create()
    server_node.update(name=server_name)
    
    switch_name = "manager_switch"
    switch_node = Node(project_id=project.project_id, name=switch_name, template="Ethernet switch",
                connector=server, x=0, y=50)
    switch_node.create()
    switch_node.update(name=switch_name)
    
    project.get_nodes()
    
    #print(switch_node)
    # Crear el enlace entre el servidor Ansible y el switch
    project.create_link(server_name, "eth0", switch_name, "Ethernet0")
    
def create_management_network(project, server) -> None:
    """
    Crea una red de gestión entre los nodos leaf, spine y server
    conectándolos a switches de gestión. Si un switch se llena,
    se crea uno nuevo automáticamente.
    """
    max_ports = 8  # Número máximo de puertos del switch
    switch_index = 1
    port_counter = 1

    def create_new_manager_switch(index):
        switch_name = f"manager_switch_{index}"
        new_switch = Node(
            project_id=project.project_id,
            name=switch_name,
            template="Ethernet switch",
            connector=server,
            x=0,
            y=50 + (index * 100)  # apila verticalmente los switches
        )
        new_switch.create()
        new_switch.update(name=switch_name)
        
        project.get_nodes()
        project.create_link(new_switch.name, "Ethernet0", management_node.name, "Ethernet7")
        print(f"Switch de gestión creado: {switch_name}")
        return new_switch

    # Crear el primer switch de gestión
    management_node = project.get_node(name="manager_switch")

    # Obtener nodos a conectar
    node_names = [
        n.name for n in project.nodes
        if n.name.startswith("leaf_") or n.name.startswith("server_") or n.name.startswith("spine_")
    ]

    for node_name in node_names:
        aux_node = project.get_node(name=node_name)

        # Si ya no hay puertos libres en el switch actual
        if (port_counter >= (max_ports - 1)):
            switch_index += 1
            management_node = create_new_manager_switch(switch_index)
            port_counter = 1  # reiniciar para el nuevo switch

        project.create_link(management_node.name, f"Ethernet{port_counter}", aux_node.name, "eth0")
        print(f"Enlace creado entre {management_node.name} (puerto {port_counter}) y {node_name}")
        port_counter += 1

def create_link_between_nodes(project, node1, node2, port1, port2) -> None:
    """
    Crea un enlace entre dos nodos en el proyecto.
    """
    project.create_link(node1.name, f"eth{port1}", node2.name, f"eth{port2}")
    print(f"Enlace creado entre {node1.name} y {node2.name}")

def main() -> None:
    # Información del servidor GNS3
    gns3_host = 'http://127.0.0.1:3080'
    username = 'admin'
    password = 'admin'

    # Crear el conector GNS3
    server = Gns3Connector(url=gns3_host, user=username, cred=password)
    print(server.get_version())

    project_name = input("Ingrese el nombre del proyecto: ")
    # Crear el proyecto
    try:
        project = Project(name=project_name, connector=server)
        project.create()
        print("Proyecto creado exitosamente. Estado del proyecto:", project.status)
    except Exception as e:
        project.get()
        project.open()
        for n in project.nodes:
            n.delete()

    # Ver templates disponibles
    templates = server.get_templates()
    print("Plantillas disponibles en el servidor GNS3:")
    for template in templates:
        print(f"- {template['name']}")

    spine_node_number = int(input("Ingrese el número de nodos spine: "))
    # Verificar si el número de nodos spine es mayor que 0
    if spine_node_number <= 0:
        raise ValueError("El número de nodos spine debe ser mayor que 0.")
    # Verificar si el número de nodos leaf es mayor que 0
    leaf_node_number = int(input("Ingrese el número de nodos leaf: "))
    if leaf_node_number <= 0:
        raise ValueError("El número de nodos leaf debe ser mayor que 0.")
    server_node_number = int(input("Ingrese el número de nodos servidor: "))
    if server_node_number <= 0:
        raise ValueError("El número de nodos servidor debe ser mayor que 0.")

    # Create spine nodes
    spine_nodes = []
    for i in range(spine_node_number):
        name = f"spine_{i+1}"
        node = Node(project_id=project.project_id, name=name, template=ROUTER_TEMPLATE,
                connector=server, x=100 + (i * 100), y=100)
        node.create()
        node.update(name=name)
        spine_nodes.append(node)

    print(f"Se han creado {spine_node_number} nodos spine.")

    # Create leaf nodes
    leaf_nodes = []
    server_nodes = []
    for i in range(leaf_node_number):
        name = f"leaf_{i+1}"
        node = Node(project_id=project.project_id, name=name, template=ROUTER_TEMPLATE,
                connector=server, x=200 + (i * 100), y=200)
        node.create()
        node.update(name=name)
        leaf_nodes.append(node)

        # Crear nodos servidor
        for j in range(server_node_number):
            server_name = f"server_{j + 1}"
            server_node = Node(project_id=project.project_id, name=server_name, template=ROUTER_TEMPLATE,
                    connector=server, x=100 + (i * 100), y=300)
            server_node.create()
            server_node.update(name=server_name)
            server_nodes.append(server_node)
            

    print(f"Se han creado {leaf_node_number} nodos leaf.")

    create_config_server(project, server)  # Crear el nodo de configuración en el servidor Ansible

    # Refrescar la lista de nodos del proyecto
    project.get_nodes()
    
    create_management_network(project, server)  # Crear la red de gestión entre los nodos leaf y los servidores
    
    # Crear enlaces entre los nodos spine y leaf
    for i in range(spine_node_number):
        spine_name = f"spine_{i + 1}"
        spine_node = project.get_node(name=spine_name)

        for j in range(leaf_node_number):
            leaf_name = f"leaf_{j + 1}"
            leaf_node = project.get_node(name=leaf_name)
            try:
                create_link_between_nodes(project, spine_node, leaf_node, j + 1, i + 1)
            except Exception as e:
                print(f"Error al crear el enlace entre {spine_name} y {leaf_name}: {e}")
        
    # Crear enlaces entre los nodos leaf y servidor
    for i in range(leaf_node_number):
        leaf_name = f"leaf_{i + 1}"
        leaf_node = project.get_node(name=leaf_name)

        for j in range(server_node_number):
            if server_node_number > 1:
                server_name = f"server_{server_node_number * i + j + 1}"
            else:
                server_name = f"server_{i + 1}"
            server_node = project.get_node(name=server_name)
            try:
                create_link_between_nodes(project, leaf_node, server_node, spine_node_number + j + 1, 1)
            except Exception as e:
                print(f"Error al crear el enlace entre {leaf_name} y {server_name}: {e}")
            
    # Start all nodes
    for node in project.nodes:
        node.start()
        print(f"Node {node.name} started.")
        
    """
    connection_port = int(input("Ingrese el puerto de conexión inicial: "))
    host_ip_number = 2
    # Configure management network
    for i in range(spine_node_number):
        spine_name = f"spine_{i + 1}"
        spine_node = project.get_node(name=spine_name)
        ip_address = f"192.168.1.{host_ip_number}"
        subnet_mask = "24"
        asyncio.run(configure_router("localhost", 5000 + connection_port, "eth0", ip_address, subnet_mask))
        host_ip_number += 1
        connection_port += 2
        
    for i in range(leaf_node_number):
        leaf_name = f"leaf_{i + 1}"
        leaf_node = project.get_node(name=leaf_name)
        ip_address = f"192.168.1.{host_ip_number}"
        subnet_mask = "24"
        asyncio.run(configure_router("localhost", 5000 + connection_port, "eth0", ip_address, subnet_mask))
        host_ip_number += 1
        connection_port += 2 * server_node_number
    """
       
    
if __name__ == "__main__":
    main()