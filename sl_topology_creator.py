from gns3fy import Gns3Connector
from gns3fy import Project, Node, Link

def create_config_server(project, server) -> None:
    """
    Crea un nodo de configuración en el servidor Ansible.
    """
    server_name = "Servidor_Ansible"
    server_node = Node(project_id=project.project_id, name=server_name, template="VPCS",
                connector=server, x=0, y=0)
    server_node.create()
    server_node.update(name=server_name)
    
    switch_name = "manager_switch"
    switch_node = Node(project_id=project.project_id, name=switch_name, template="Ethernet switch",
                connector=server, x=0, y=50)
    switch_node.create()
    switch_node.update(name=switch_name)
    
    # Crear el enlace entre el servidor Ansible y el switch
    link = Link(
        project_id=project.project_id,
        connector=server,
        nodes=[
            {"node_id": server_node.node_id, "adapter_number": 0, "port_number": 0},
            {"node_id": switch_node.node_id, "adapter_number": 0, "port_number": 0}
        ]
    )
    link.create()
    
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
        
        link = Link(project_id=project.project_id, connector=server,
                    nodes=[
                        {"node_id":new_switch.node_id, "adapter_number": 0, "port_number": 0},
                        {"node_id":management_node.node_id, "adapter_number": 0, "port_number": 7}
                    ])
        link.create()
        print(f"Switch de gestión creado: {switch_name}")
        return new_switch

    # Crear el primer switch de gestión
    management_node = project.get_node(name="manager_switch")

    # Obtener nodos a conectar
    node_names = [
        n.name for n in project.nodes
        if n.name.startswith("leaf_") or n.name.startswith("base_switch_") or n.name.startswith("spine_")
    ]

    for node_name in node_names:
        aux_node = project.get_node(name=node_name)

        # Si ya no hay puertos libres en el switch actual
        if (port_counter >= (max_ports - 1)):
            switch_index += 1
            management_node = create_new_manager_switch(switch_index)
            port_counter = 1  # reiniciar para el nuevo switch

        link = Link(
            project_id=project.project_id,
            connector=server,
            nodes=[
                {"node_id": management_node.node_id, "adapter_number": 0, "port_number": port_counter},
                {"node_id": aux_node.node_id, "adapter_number": 0, "port_number": 0}
            ]
        )
        link.create()
        print(f"Enlace creado entre {management_node.name} (puerto {port_counter}) y {node_name}")
        port_counter += 1

def create_link_between_nodes(project, server, node1, node2, port1, port2) -> None:
    """
    Crea un enlace entre dos nodos en el proyecto.
    """
    link = Link(
        project_id=project.project_id,
        connector=server,
        nodes=[
            {"node_id": node1.node_id, "adapter_number": 0, "port_number": port1},
            {"node_id": node2.node_id, "adapter_number": 0, "port_number": port2}
        ]
    )
    link.create()
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

    # Crear nodos spine
    for i in range(spine_node_number):   
        name = f"spine_{i+1}"
        node = Node(project_id=project.project_id, name=name, template="Ethernet switch",
                    connector=server, x=100 + (i * 100), y=100)
        node.create()
        node.update(name=name)

    print(f"Se han creado {spine_node_number} nodos spine.")

    # Crear nodos leaf
    for i in range(leaf_node_number):
        name = f"leaf_{i + 1}"
        node = Node(project_id=project.project_id, name=name, template="Ethernet switch",
                    connector=server, x=100 + (i * 100), y=200)
        node.create()
        node.update(name=name)

        # Crear nodos servidor
        for j in range(server_node_number):
            server_name = f"server_{j + 1}"
            server_node = Node(project_id=project.project_id, name=server_name, template="VPCS",
                    connector=server, x=100 + (i * 100), y=300)
            server_node.create()
            server_node.update(name=server_name)
            
            base_name = f"base_switch_{i + 1}"
            base_switch = Node(project_id=project.project_id, name=base_name, template="Ethernet switch",
                    connector=server, x=100 + (i * 100), y=400)
            base_switch.create()
            base_switch.update(name=base_name)
            # Crear el enlace entre el servidor y el switch base
            link = Link(
                project_id=project.project_id,
                connector=server,
                nodes=[
                    {"node_id": server_node.node_id, "adapter_number": 0, "port_number": 0},
                    {"node_id": base_switch.node_id, "adapter_number": 0, "port_number": 1}
                ]
            )
            link.create()

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
                create_link_between_nodes(project, server, spine_node, leaf_node, j + 1, i + 1)
            except Exception as e:
                print(f"Error al crear el enlace entre {spine_name} y {leaf_name}: {e}")
        
    # Crear enlaces entre los nodos leaf y servidor
    for i in range(leaf_node_number):
        leaf_name = f"leaf_{i + 1}"
        leaf_node = project.get_node(name=leaf_name)

        for j in range(server_node_number):
            server_name = f"base_switch_{i + 1}"
            server_node = project.get_node(name=server_name)
            try:
                create_link_between_nodes(project, server, leaf_node, server_node, spine_node_number + j + 1, 2)
            except Exception as e:
                print(f"Error al crear el enlace entre {leaf_name} y {server_name}: {e}")
        
    # Refrescar la lista de enlaces en el proyecto
    project.get_links()
    
if __name__ == "__main__":
    main()