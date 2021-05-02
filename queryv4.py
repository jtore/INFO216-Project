from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, XML
import re

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")


# java -server -Xmx4g -jar blazegraph.jar


sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT DISTINCT ?item1 ?item2 ?value  WHERE {

        ?item1 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation1 .
        ?superAnnotation1 nhterm:hasEntity ?value . 
    
        ?item2 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation2 .
        ?superAnnotation2 nhterm:hasEntity ?value . 
    }
    LIMIT 10
""")

sparql.setReturnFormat(JSON)
teste = sparql.query().convert()

#for result in teste["results"]["bindings"]:
 #   print(result)

# -------------Items------------#

"""
AnchorOf

Return two items where the items match on having a Annotation 
where the Annotation is nhterm:anchorOf 
and the value is the same in both items
"""

sparql.setQuery("""

PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT DISTINCT ?item1 ?item2 ?value sourceIRLValue1  sourceIRLValue1WHERE {
    
        ?item1 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation1 .
        ?superAnnotation1 nhterm:anchorOf ?value . 
        nhterm:sourceIRL ?sourceIRLValue1 .
    
        ?item2 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation2 .
        ?superAnnotation2 nhterm:anchorOf ?value .
        nhterm:sourceIRL ?sourceIRLValue2 .

         
        }
    LIMIT 50
""")

sparql.setReturnFormat(JSON)
test = sparql.query().convert()

for result in test["results"]["bindings"]:
    print(result)


"""Return sourceDateTime for every item graph"""

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

"""Return items ordered by date and organized by items grouped from date and time"""

d = 18

sparql.setQuery("""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX nhterm: <https://newshunter.uib.no/term#>
        SELECT ?item ?dt ?year ?month ?day ?hours ?minutes 
            WHERE
            {
                ?item a nhterm:Item ;
                nhterm:sourceDateTime ?dt .
                bind(year(?dt) as ?year)
                bind(month(?dt) as ?month)
                bind(day(?dt) as ?day)
                bind(hours(?dt) as ?hours)
                bind(minutes(?dt) as ?minutes)
                FILTER((?year = 2020 && ?month = 9 && ?day = %s)) 
            }
        ORDER BY ?year ?month ?day ?hours ?minutes

"""%d)

""" Constructs a graph object from the return value of the above query"""
time_results = sparql.query().convert()
#for content in time_results["results"]["bindings"]:
    #print(content)


def annotation_lifter(item):
    for content in item["results"]["bindings"]:
        #print(content)
        item = content["item"]["value"]

        sparql.setQuery("""
        PREFIX nhterm: <https://newshunter.uib.no/term#>
            SELECT DISTINCT ?annotation_property ?annotation_value WHERE {
                ?item a nhterm:Item;
                ?p ?o;
                nhterm:hasAnnotation ?annotation .
                ?annotation ?annotation_property ?annotation_value .
        FILTER(STR(?item) ="%s")
        }
        """%item)
        sparql.setReturnFormat(JSON)
        item = sparql.query().convert()
        #for result in item["results"]["bindings"]:
          #  print(result)

        #print(result["annot_p"]["value"])
        #print(result["annot_o"]["value"])

#annotation_lifter(time_results)

'''
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
'''


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
#for s, p, o in output_graph.triples((None, RDF.type, nhterm.Item)):
 #   g.add((Event, nhterm.describedBy, s))

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


# java -server -Xmx4g -jar blazegraph.jar
