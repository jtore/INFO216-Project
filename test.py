from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import random
import string
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, XML
import re


# java -server -Xmx4g -jar blazegraph.jar

# output_dict = {"time": item_output["time"]["value"], "irl": item_output["irl"]["value"],
#              "anchor": item_output["anchor"]["value"], "annotator": item_output["annotator"]["value"],
#              "collection": item_output["collection"]["value"]}

# print(output_dict)


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


def item_lifter(item):
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
                    LIMIT 1000
            """ % item)
    sparql.setReturnFormat(JSON)

    return_block = sparql.query().convert()
    for result in return_block["results"]["bindings"]:
        return result


sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT DISTINCT ?item1 ?item2 ?entity WHERE {

        ?item1 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation1 .
        ?superAnnotation1 nhterm:hasEntity ?entity . 

        ?item2 a nhterm:Item ;
        nhterm:hasAnnotation ?superAnnotation2 .
        ?superAnnotation2 nhterm:hasEntity ?entity . 
        FILTER(?item1 != ?item2)
        
    }

    LIMIT 1000
""")
sparql.setReturnFormat(JSON)
entity_graph = sparql.query().convert()

dict = {}
item_lifter_output_list = []

for items in entity_graph["results"]["bindings"]:
    item1 = items["item1"]["value"]
    item2 = items["item2"]["value"]
    entity = items["entity"]["value"]

    if not dict.get(entity):
        dict[entity] = [item1, item2]
    else:
        acc = dict.get(entity)
        if item1 not in acc:
            dict[entity].append(item1)
        if item2 not in acc:
            dict[entity].append(item2)

# For each entity and the list containing items related to that entity
for k, v in dict.items():
    #print("-- Item --")

    # Make a list to store the output from item_lifter when applied to each item related to an entity
    item_lifter_output_list = []
    print("Key:", k, "value:", v)

    # For each item in the list of items related to an entity, apply the item_lifter function
    for result in v:
        item_output = item_lifter(result)
        # Append the result to item_lifter_output_list
        item_lifter_output_list.append(item_output)

    #print(item_list)

    time_list = []
    irl_list = []
    anchor_list = []
    annotator_list = []
    collection = []

    # Takes the different value properties and adds them in separate lists
    for result in item_lifter_output_list:
        time_list.append(result["time"]["value"])
        irl_list.append(result["irl"]["value"])
        anchor_list.append(result["anchor"]["value"])
        collection.append(result["collection"]["value"])

    g = Graph()
    print(time_list)
    print(irl_list)
    print(anchor_list)
    print(collection)


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

    Event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)

    # Event hash
    g.add((Event, RDF.type, nhterm.Event))

    # nhterm:DescribedBy
    for result in v:
        g.add((Event, nhterm.describedBy, URIRef(result)))

    # nhterm:hasDescriptor
    #g.add((Event, nhterm.hasDescriptor, bn))

    # nhterm:hasDescriber
    for annotator in annotator_list:
        g.add((bn, nhterm.hasDescriber, URIRef(annotator)))

    # nhterm:Descriptor
    g.add((Event, nhterm.hasDescriptor, bn2))
    g.add((bn2, RDF.type, nhterm.Descriptor))


    # ntherm:anchorOf
    for anchor in anchor_list:
        g.add((bn2, nhterm.anchorOf, Literal(anchor, datatype=XSD.string)))

    # nhterm:hasDescriber
    for collec in collection:
        g.add((bn2, nhterm.hasDescriber, URIRef(collec)))

    # nhterm:hasEntity
    #g.add((bn2, nhterm.hasEntity, URIRef(entity)))

    # nhterm:sourceIRL
    for irl in irl_list:
        g.add((bn2, nhterm.sourceIRL, URIRef(irl)))

    # SourceDateTime
    for time in time_list:
        g.add((bn2, nhterm.sourceDateTime, URIRef(time)))

    print(g.serialize(format="ttl").decode("utf-8"))


# java -server -Xmx4g -jar blazegraph.jar