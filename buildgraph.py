from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL

g = Graph()
# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource")
g.bind("nh", nh)
nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)
bn = BNode()
bn2 = BNode()

Event = URIRef("Event-resouce")
Describer = URIRef("Describer")
Relation = URIRef("relation")
RelationFrom = URIRef("relationFrom")
RelationTo = URIRef("RelationTo")


g.add((Event, RDF.type, nhterm.Event))
g.add((Event, nhterm.describedBy, Literal("ID")))
g.add((Event, nhterm.hasDescriptor, bn))

g.add((bn, RDF.type, nhterm.RelationDescriptor))
g.add((bn, nhterm.hasDescriber, Describer))
g.add((bn, nhterm.hasRelation, Relation))
g.add((bn, nhterm.relationFrom, RelationFrom))
g.add((bn, nhterm.relationTo, RelationTo))

g.add((Event, nhterm.hasDescriptor, bn2))
g.add((bn2, RDF.type, nhterm.Descriptor))
g.add((bn2, nhterm.anchorOf, Literal("String", datatype=XSD.string)))
g.add((bn2, nhterm.hasDescriber, Describer))
g.add((bn2, nhterm.hasEntity, Literal("Entity")))
g.add((bn2, nhterm.hasSourceIdentifier, Literal("Numbers", datatype=XSD.string)))

print(g.serialize(format="ttl").decode("utf-8"))
