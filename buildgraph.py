from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from random import randint


def generate_hash():
    start_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))

    _2sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _3sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _4sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))

    end_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(12))

    _hash = start_sect + "-" + _2sect + "-" + _3sect + "-" + _4sect + "-" + end_sect
    return _hash


g = Graph()
# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource#")
g.bind("nh", nh)
nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)
bn = BNode()
bn2 = BNode()

event_hash_value = generate_hash()
Event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)
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
