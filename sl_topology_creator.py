from gns3fy import Gns3Connector
from gns3fy import Project, Node

SERVER_TEMPLATE = "Network Automation"
ROUTER_TEMPLATE = "FRR 8.2.2"

def create_config_server(project, server) -> None:
    """
    Creates a configuration server node in the GNS3 project.
    This server is used to manage the configuration of other nodes.
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
    
    # Create link between the server and the switch
    project.create_link(server_name, "eth0", switch_name, "Ethernet0")
    
def create_management_network(project, server) -> None:
    """
    Creates a management network between leaf, spine, and server nodes
    by connecting them to management switches. If a switch is full,
    a new one is automatically created.
    """
    max_ports = 8  # Maximum number of ports per switch
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
            y=50 + (index * 100)
        )
        new_switch.create()
        new_switch.update(name=switch_name)
        
        project.get_nodes()
        project.create_link(new_switch.name, "Ethernet0", management_node.name, "Ethernet7")
        print(f"Switch de gestión creado: {switch_name}")
        return new_switch

    # Create the first management switch
    management_node = project.get_node(name="manager_switch")

    # Get the list of nodes to connect
    node_names = [
        n.name for n in project.nodes
        if n.name.startswith("leaf_") or n.name.startswith("server_") or n.name.startswith("spine_")
    ]

    for node_name in node_names:
        aux_node = project.get_node(name=node_name)

        # Check if the current switch is full
        if (port_counter >= (max_ports - 1)):
            switch_index += 1
            management_node = create_new_manager_switch(switch_index)
            port_counter = 1  # reset port counter for the new switch

        project.create_link(management_node.name, f"Ethernet{port_counter}", aux_node.name, "eth0")
        print(f"Enlace creado entre {management_node.name} (puerto {port_counter}) y {node_name}")
        port_counter += 1

def create_link_between_nodes(project, node1, node2, port1, port2) -> None:
    """
    Creates a link between two nodes in the GNS3 project.
    """
    project.create_link(node1.name, f"eth{port1}", node2.name, f"eth{port2}")
    print(f"Enlace creado entre {node1.name} y {node2.name}")

def main() -> None:
    # GNS3 server connection details
    gns3_host = 'http://127.0.0.1:3080'
    username = 'admin'
    password = 'admin'

    # Crear el conector GNS3
    server = Gns3Connector(url=gns3_host, user=username, cred=password)
    print(server.get_version())

    project_name = input("Ingrese el nombre del proyecto: ")
    # Create a new project or delete the existing one
    try:
        project = Project(name=project_name, connector=server)
        project.create()
        print("Proyecto creado exitosamente. Estado del proyecto:", project.status)
    except Exception as e:
        project.get()
        project.open()
        for n in project.nodes:
            n.delete()

    # Show available templates
    templates = server.get_templates()
    print("Plantillas disponibles en el servidor GNS3:")
    for template in templates:
        print(f"- {template['name']}")

    spine_node_number = int(input("Ingrese el número de nodos spine: "))
    # Check if the number of spine nodes is greater than 0
    if spine_node_number <= 0:
        raise ValueError("El número de nodos spine debe ser mayor que 0.")
    
    leaf_node_number = int(input("Ingrese el número de nodos leaf: "))
    # Check if the number of leaf nodes is greater than 0
    if leaf_node_number <= 0:
        raise ValueError("El número de nodos leaf debe ser mayor que 0.")
    
    server_node_number = int(input("Ingrese el número de nodos servidor: "))
    # Check if the number of server nodes is greater than 0
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

        # Create server nodes
        for j in range(server_node_number):
            server_name = f"server_{j + 1}"
            server_node = Node(project_id=project.project_id, name=server_name, template=ROUTER_TEMPLATE,
                    connector=server, x=100 + (i * 100), y=300)
            server_node.create()
            server_node.update(name=server_name)
            server_nodes.append(server_node)
            

    print(f"Se han creado {leaf_node_number} nodos leaf.")

    create_config_server(project, server)  # Create the configuration server node

    # Refresh the project to get the latest nodes
    project.get_nodes()
    
    create_management_network(project, server)  # Create the management network
    
    # Create links between spine and leaf nodes
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
        
    # Create links between leaf and server nodes
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
    
if __name__ == "__main__":
    main()