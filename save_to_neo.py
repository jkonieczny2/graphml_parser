
from pygraphml import GraphMLParser as GParse
import os
from neo4j.v1 import GraphDatabase


path = '/home/joshua/projects/graphml_parser/samples/case_4a.graphml'

#Create parser object
parser = GParse()
g = parser.parse(path)

#Collect all nodes
nodes = g.nodes()

#Instantiate connection to Neo4J
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "jkon-611"))

#Function to extract all attributes
def upload_node(node):
	attrs = node.attributes()

	node_type = attrs['type'].value

	node_attributes = {k:attrs[k].value for k in attrs}
	node_attributes['id'] = node.id
	neo_attributes = create_neo_attributes(node_attributes)
	
	neo_query = create_neo_node(node_type , neo_attributes)

	return neo_query


def create_neo_attributes(attrs):
	"""
	Assumption is that attrs is a dictionary of attributes
	"""
	neo_string = "{"

	for k in attrs:
		new_attr =  "%s: '%s' ,"%(k,attrs[k])
		neo_string += new_attr

	final_string = neo_string[:-1] + "}"

	return final_string

def create_neo_node(node_type , attributes):
	#Need to clean out invalid characters
	node_type = node_type.replace(" " , "_")
	attributes = attributes.replace("/","").replace("\\" , '')

	neo_string = "MERGE (a:%s %s)"%(node_type, attributes)

	return neo_string

#Function to extract parent and child ID from edges
def generate_edge_query(edge):
	parent_type = edge.parent().attributes()['type'].value.replace(" " , "_")
	child_type = edge.child().attributes()['type'].value.replace(" " , "_")

	parent_id = edge.parent().id
	child_id = edge.child().id
	edge_type = edge.attributes()['text'].value

	edge_info = (parent_type , child_type , parent_id , child_id , edge_type)

	query = 'MATCH (parent:%s),(child:%s) WHERE parent.id = "%s" and child.id = "%s" MERGE (parent)-[r:%s]->(child)'%(edge_info)

	return query

	

###Testing Nodes
test_node = nodes[0]
node_query = upload_node(test_node)

###Testing edges
edges = g.edges()
test_edge = edges[0]
edge_query = generate_edge_query(test_edge)

###Test loading some information to neo
with driver.session() as session:
    tx = session.begin_transaction()
    for node in nodes:
    	node_query = upload_node(node)
    	tx.run(node_query)

    for edge in edges:
    	edge_query = generate_edge_query(edge)
    	print edge_query
    	tx.run(edge_query)

    tx.commit()




