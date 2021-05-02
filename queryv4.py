from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, XML
import re


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
bn3 = BNode()
event_hash_value = generate_hash()


# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")


# java -server -Xmx4g -jar blazegraph.jar

def item_lifter(i1, i2):

    item_list = [i1, i2]
    for i in item_list:

        sparql.setQuery("""
                PREFIX nhterm: <https://newshunter.uib.no/term#>
                SELECT ?time ?text ?irl ?anchor ?contributor ?annotator ?entity ?collection
                    WHERE
                    {
                     
                        ?item a nhterm:Item ;
                        nhterm:originalText ?o ;
                        nhterm:sourceDateTime ?time ;
                        nhterm:sourceIRL ?irl ;
                        nhterm:hasContributor ?contributor ;
                        nhterm:inCollection ?collection ;
                        nhterm:hasAnnotation ?superAnnotation1 .
                        ?superAnnotation1 nhterm:anchorOf ?anchor .
                        ?superAnnotation1 nhterm:hasAnnotator ?annotator .
                        ?superAnnotation1 nhterm:hasEntity ?entity .
                        
                        FILTER(STR(?item) ="%s")
                    }
                    LIMIT 2
            """%i)
        sparql.setReturnFormat(JSON)

        if i == i1:
            item1 = sparql.query().convert()
            for result in item1["results"]["bindings"]:
                return result

        if i == i2:
            item2 = sparql.query().convert()
            for result in item2["results"]["bindings"]:
                return result




sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT DISTINCT ?item1 ?item2 ?value  WHERE {

        ?item1 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation1 .
        ?superAnnotation1 nhterm:hasEntity ?value . 
    
        ?item2 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation2 .
        ?superAnnotation2 nhterm:hasEntity ?value . 
        FILTER(?item1 != ?item2)
    }
    LIMIT 10
""")


sparql.setReturnFormat(JSON)
entity = sparql.query().convert()


for items in entity["results"]["bindings"]:
    item1 = items["item1"]["value"]
    item2 = items["item2"]["value"]
    item_output = item_lifter(item1, item2)

    time = item_output["time"]["value"]
    irl = item_output["irl"]["value"]
    anchor = item_output["anchor"]["value"]
    annotator = item_output["annotator"]["value"]
    entity = item_output["entity"]["value"]
    collection = item_output["collection"]["value"]
    #print(time, irl, anchor)
    #anchorOf_lifter(item1, item2)

# ------------------- Make Event graph -------------------

    Event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)
    Describer = URIRef("Describer")
    Relation = URIRef("relation")
    RelationFrom = URIRef("relationFrom")
    RelationTo = URIRef("RelationTo")

    #
    g.add((Event, RDF.type, nhterm.Event))

    # DescribedBy
    g.add((Event, nhterm.describedBy, URIRef(item1)))
    g.add((Event, nhterm.describedBy, URIRef(item2)))

    # hasDescriptor
    g.add((Event, nhterm.hasDescriptor, bn))

    g.add((bn, RDF.type, nhterm.RelationDescriptor))

    # nhterm:hasDescriber
    g.add((bn, nhterm.hasDescriber, URIRef(annotator)))

    g.add((bn, nhterm.hasRelation, Relation))
    g.add((bn, nhterm.relationFrom, URIRef(entity)))
    g.add((bn, nhterm.relationTo, URIRef(entity)))

    # a nhterm descriptor
    g.add((Event, nhterm.hasDescriptor, bn2))
    g.add((bn2, RDF.type, nhterm.Descriptor))

    # anchorOf
    g.add((bn2, nhterm.anchorOf, Literal(anchor, datatype=XSD.string)))

    #hasDescriber
    g.add((bn2, nhterm.hasDescriber, URIRef(collection)))

    #hasEntity
    g.add((bn2, nhterm.hasEntity, URIRef(entity)))

    #sourceIRL
    g.add((bn2, nhterm.sourceIRL, URIRef(irl)))

    #g.add((bn2, nhterm.hasSourceIdentifier, Literal("Numbers", datatype=XSD.string)))

    print(g.serialize(format="ttl").decode("utf-8"))


# java -server -Xmx4g -jar blazegraph.jar


# -------------Items------------#

"""
AnchorOf

Return two items where the items match on having a Annotation 
where the Annotation is nhterm:anchorOf 
and the value is the same in both items
"""

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