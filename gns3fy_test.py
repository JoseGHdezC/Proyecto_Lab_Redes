from gns3fy import Gns3Connector
from gns3fy import Project, Node, Link

# Información del servidor GNS3
gns3_host = 'http://127.0.0.1:3080'
username = 'admin'
password = 'admin'

# Crear el conector GNS3
server = Gns3Connector(url=gns3_host, user=username, cred=password)
print("Versión del servidor:", server.get_version())

# Crear el proyecto
try:
    project = Project(name="MiNuevoPoyecto", connector=server)
    project.create()
    print("Proyecto creado exitosamente.")
except Exception as e:
    # Si ya existe el proyecto, se refresca y se eliminan los nodos existentes.
    project.get()
    for n in project.nodes:
        n.delete()

# Ver templates disponibles
templates = server.get_templates()
print("Plantillas disponibles en el servidor GNS3:")
for template in templates:
    print(f"- {template['name']}")

# Crear nodos
# Nodo 1: spine (usamos "Ethernet switch" como ejemplo)
name_spine = "spine"
node_spine = Node(project_id=project.project_id, name=name_spine, template="Ethernet switch",
                   connector=server, x=100, y=100)
node_spine.create()
node_spine.update(name=name_spine)

# Nodo 2: leaf (usamos "Ethernet switch" como ejemplo)
name_leaf = "leaf"
node_leaf = Node(project_id=project.project_id, name=name_leaf, template="Ethernet switch",
                  connector=server, x=300, y=100)
node_leaf.create()
node_leaf.update(name=name_leaf)

# Nodo 3: servidor (por ejemplo, usando el template "VPCS", ajustar si usas otro)
name_server = "servidor"
node_server = Node(project_id=project.project_id, name=name_server, template="VPCS",
                   connector=server, x=200, y=250)
node_server.create()
node_server.update(name=name_server)

# Refrescar la lista de nodos del proyecto
project.get_nodes()

# Verificar que se hayan actualizado los nodos
print("Nodos del proyecto:")
for n in project.nodes:
    print(f"- {n.name} (ID: {n.node_id})")

# Crear enlace entre spine y leaf
link_spine_leaf = Link(
    project_id=project.project_id,
    connector=server,
    nodes=[
        {"node_id": node_spine.node_id, "adapter_number": 0, "port_number": 0},
        {"node_id": node_leaf.node_id, "adapter_number": 0, "port_number": 0}
    ]
)
link_spine_leaf.create()

# Crear enlace entre leaf y servidor
link_leaf_server = Link(
    project_id=project.project_id,
    connector=server,
    nodes=[
        {"node_id": node_leaf.node_id, "adapter_number": 0, "port_number": 1},
        {"node_id": node_server.node_id, "adapter_number": 0, "port_number": 0}
    ]
)
link_leaf_server.create()

# Refrescar la lista de enlaces en el proyecto
project.get_links()

# Mostrar estado final del proyecto, los nodos y los enlaces
print("Proyecto creado exitosamente.")
print("Estado del proyecto:", project.status)
print("Enlaces del proyecto:")
for l in project.links:
    node1_id = l.nodes[0]['node_id']
    node2_id = l.nodes[1]['node_id']
    # Buscar el nombre de los nodos usando la lista actualizada
    node1_name = next((n.name for n in project.nodes if n.node_id == node1_id), "Desconocido")
    node2_name = next((n.name for n in project.nodes if n.node_id == node2_id), "Desconocido")
    print(f"- Enlace entre {node1_name} y {node2_name}")