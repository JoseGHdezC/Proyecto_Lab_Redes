from gns3fy import Gns3Connector
from gns3fy import Project, Node, Link

# Información del servidor GNS3
gns3_host = 'http://127.0.0.1:3080'
username = 'admin'
password = 'admin'

# Crear el conector GNS3
server = Gns3Connector(url=gns3_host, user=username, cred=password)
print(server.get_version())

# Crear el proyecto
try:
    project = Project(name="MiNuevoPoyecto", connector=server)
    project.create()
    print("Proyecto creado exitosamente.")
except Exception as e:
    project.get()
    for n in project.nodes:
        n.delete()

# Ver templates disponibles
templates = server.get_templates()
print("Plantillas disponibles en el servidor GNS3:")
for template in templates:
    print(f"- {template['name']}")

# Crear nodos
# Nodo 1: spine
name = "spine"
node = Node(project_id=project.project_id, name=name, template="Ethernet switch",
            connector=server, x=100, y=100)
node.create()
node.update(name=name)

# Nodo 2: leaf
name2 = "leaf"
node2 = Node(project_id=project.project_id, name=name2, template="Ethernet switch",
             connector=server, x=200, y=100)
node2.create()
node2.update(name=name2)

# Refrescar la lista de nodos del proyecto
project.get_nodes()

# Crear el enlace entre los nodos enviando una lista de diccionarios con la información
link = Link(
    project_id=project.project_id,
    connector=server,
    nodes=[
        {"node_id": node.node_id, "adapter_number": 0, "port_number": 0},
        {"node_id": node2.node_id, "adapter_number": 0, "port_number": 0}
    ]
)
link.create()

# Mostrar el estado final del proyecto y enlaces
print("Proyecto creado exitosamente.")
print("Estado del proyecto:", project.status)

# Verificar que se hayan actualizado los nodos
print("Nodos del proyecto:")
for n in project.nodes:
    print(f"- {n.name} (ID: {n.node_id})")
    
project.get_links()

print("Enlaces del proyecto:")
for l in project.links:
    node1_id = l.nodes[0]['node_id']
    node2_id = l.nodes[1]['node_id']
    
    # Find the node names using the project nodes
    node1_name = next((n.name for n in project.nodes if n.node_id == node1_id), "Unknown")
    node2_name = next((n.name for n in project.nodes if n.node_id == node2_id), "Unknown")
    
    print(f"- Enlace entre {node1_name} y {node2_name}")
