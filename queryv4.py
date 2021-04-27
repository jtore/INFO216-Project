import rdflib.plugins.sparql.parser
from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, XML

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.


g = Graph()
# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource")
g.bind("nh", nh)
nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)
bn = BNode()

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")

#anchorof_value = input("Input anchorOf value for your graph: ")

# -------------Items------------#

"""
Return two items where the items match on having a Annotation 
where the Annotation is nhterm:anchorOf 
and the value is the same in both items
"""

sparql.setQuery("""

PREFIX nhterm: <https://newshunter.uib.no/term#>
SELECT DISTINCT ?item1 ?item2 WHERE {

    ?item1 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation1 .
    ?superAnnotation1 nhterm:anchorOf "Tesla" . 

    ?item2 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation2 .
    ?superAnnotation2 nhterm:anchorOf "Tesla" . 
    }
    LIMIT 50
""")

sparql.setReturnFormat(JSON)
test = sparql.query().convert()

# -----------------SourceDateTime----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?s ?p ?o
    WHERE
    {
        ?s a nhterm:Item ;
        nhterm:sourceDateTime ?o .
    }
""")
sparql.setReturnFormat(JSON)
sourceDateTime = sparql.query().convert()


sparql.setQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?item ?dt ?year ?month ?day ?hours ?minutes 
    WHERE
    {
        ?item a nhterm:Item ;
        nhterm:sourceDateTime ?dt
        bind(year(?dt) as ?year)
        bind(month(?dt) as ?month)
        bind(day(?dt) as ?day)
        bind(hours(?dt) as ?hours)
        bind(minutes(?dt) as ?minutes)
    }
        ORDER BY ?year ?month ?day ?hours ?minutes
        LIMIT 1


""")

time_results = sparql.query().convert()
for result in time_results["results"]["bindings"]:
    item = result["item"]["value"]
    sparql.setQuery("""
           DESCRIBE ?item WHERE
           {
              FILTER(STR(?item) = "%s")
           }
      """ % item)
    sparql.setReturnFormat(XML)

output_graph = sparql.queryAndConvert()
serialized_graph = output_graph.serialize(format="ttl").decode("utf-8")
print(serialized_graph)




# starte Blazegraph server:  java -server -Xmx4g -jar blazegraph.jar

# ------------------- Make Event graph -------------------


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

# Adding item to graph in describedBy attribute
for s, p, o in output_graph.triples((None, RDF.type, nhterm.Item)):
    g.add((Event, nhterm.describedBy, s))

# Annotation
#for s,p,o in output_graph.triples((None, nhterm.hasAnnotation, None)):
    #print(s,p,o)

# sourceDateTime
#for s,p,o in output_graph.triples((None, nhterm.sourceDateTime, None)):
 #   print(s,p,o)

# sourceIRL
#for s,p,o in output_graph.triples((None, nhterm.sourceIRL, None)):
#   print(s,p,o)



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

#print(g.serialize(format="ttl").decode("utf-8"))


# starte Blazegraph server:  java -server -Xmx4g -jar blazegraph.jar
