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
    project.open()
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
node_spine = Node(project_id=project.project_id, name=name_spine, template="FRR",
                   connector=server, x=100, y=100)
node_spine.create()
node_spine.update(name=name_spine)

# Nodo 2: leaf (usamos "Ethernet switch" como ejemplo)
name_leaf = "leaf"
node_leaf = Node(project_id=project.project_id, name=name_leaf, template="FRR",
                  connector=server, x=300, y=100)
node_leaf.create()
node_leaf.update(name=name_leaf)

# Nodo 3: servidor (por ejemplo, usando el template "VPCS", ajustar si usas otro)
name_server = "servidor"
node_server = Node(project_id=project.project_id, name=name_server, template="Server",
                   connector=server, x=200, y=250)
node_server.create()
node_server.update(name=name_server)

# Refrescar la lista de nodos del proyecto
project.get_nodes()
#project.start_nodes()

# Create link
project.create_link(name_spine, "eth1", name_leaf, "eth1")

# Crear enlace entre leaf y servidor
project.create_link(name_leaf, "eth2", name_server, "eth1")