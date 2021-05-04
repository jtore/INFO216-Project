from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, XML
import re


# java -server -Xmx4g -jar blazegraph.jar


# Generate a hash to use as a ID for a nhterm:Event
def generate_hash():
    start_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
    _2sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _3sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _4sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    end_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(12))

    _hash = start_sect + "-" + _2sect + "-" + _3sect + "-" + _4sect + "-" + end_sect
    return _hash


event_hash_value = generate_hash()

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")


def item_lifter(i1, i2):
    item_list = [i1, i2]
    for i in item_list:

        sparql.setQuery("""
                PREFIX nhterm: <https://newshunter.uib.no/term#>
                SELECT ?time ?text ?irl ?anchor ?contributor ?annotator ?collection
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
                    FILTER(STR(?item) ="%s")
                    }
                    LIMIT 5
            """ %i)
        sparql.setReturnFormat(JSON)

        if i == i1:
            return_item1 = sparql.query().convert()
            for result in return_item1["results"]["bindings"]:
                return result

        if i == i2:
            return_item2 = sparql.query().convert()
            for result in return_item2["results"]["bindings"]:
                return result


sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT DISTINCT ?item1 ?item2 ?entity1 ?entity2 WHERE {

        ?item1 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation1 .
        ?superAnnotation1 nhterm:hasEntity ?entity1 . 

        ?item2 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation2 .
        ?superAnnotation2 nhterm:hasEntity ?entity2 . 
        FILTER(?item1 != ?item2)
        FILTER(?entity1 = ?entity2)
    }

    LIMIT 5
""")
sparql.setReturnFormat(JSON)
entity_graph = sparql.query().convert()

g = Graph()

for items in entity_graph["results"]["bindings"]:
    item1 = items["item1"]["value"]
    item2 = items["item2"]["value"]
    #print("entity1", items["entity1"]["value"])
    #print("entity2", items["entity2"]["value"])

    item_output = item_lifter(item1, item2)

    output_dict = {"time": item_output["time"]["value"], "irl": item_output["irl"]["value"],
                   "anchor": item_output["anchor"]["value"], "annotator": item_output["annotator"]["value"],
                   "collection": item_output["collection"]["value"]}

    # ------------------- Make Event graph -------------------

    # Make graph

    # Bind prefixes and namespaces to use

    # nh
    nh = Namespace("https://newshunter.uib.no/resource#")
    g.bind("nh", nh)

    # nhterm
    nhterm = Namespace("https://newshunter.uib.no/term#")
    g.bind("nhterm", nhterm)

    # Blank nodes
    bn = BNode()
    bn2 = BNode()
    bn3 = BNode()

    Event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)

    # Event hash
    g.add((Event, RDF.type, nhterm.Event))

    # nhterm:DescribedBy
    g.add((Event, nhterm.describedBy, URIRef(item1)))
    g.add((Event, nhterm.describedBy, URIRef(item2)))

    # nhterm:hasDescriptor
    g.add((Event, nhterm.hasDescriptor, bn))

    # nhterm:hasDescriber
    g.add((bn, nhterm.hasDescriber, URIRef(output_dict["annotator"])))

    # nhterm:Descriptor
    g.add((Event, nhterm.hasDescriptor, bn2))
    g.add((bn2, RDF.type, nhterm.Descriptor))

    # ntherm:anchorOf
    g.add((bn2, nhterm.anchorOf, Literal(output_dict["anchor"], datatype=XSD.string)))

    # nhterm:hasDescriber
    g.add((bn2, nhterm.hasDescriber, URIRef(output_dict["collection"])))

    # nhterm:hasEntity
    #g.add((bn2, nhterm.hasEntity, URIRef(entity)))

    # nhterm:sourceIRL
    g.add((bn2, nhterm.sourceIRL, URIRef(output_dict["irl"])))

print(g.serialize(format="ttl").decode("utf-8"))

# java -server -Xmx4g -jar blazegraph.jar


