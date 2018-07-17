
from pygraphml import GraphMLParser as GParse
import os

path = '/home/joshua/projects/graphml_parser/samples/case_4a.graphml'

#Create parser object
parser = GParse()
g = parser.parse(path)

#Explore a node
node = g.nodes()[1]

#This is a dictionary
attrs = node.attributes()

print node._edges


