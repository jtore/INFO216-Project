from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import uuid_generator


# java -server -Xmx4g -jar blazegraph.jar


# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")


def item_lifter(external_item):
    sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
        SELECT ?time ?text ?irl ?anchor ?contributor ?annotator ?collection
            WHERE
            {
            ?item a nhterm:Item ;
                nhterm:originalText ?text ;
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
            """ % external_item)
    sparql.setReturnFormat(JSON)

    return_block = sparql.query().convert()
    for result in return_block["results"]["bindings"]:
        return result


def make_entity_item_dict():
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

    entity_item_dict = {}

    for items in entity_graph["results"]["bindings"]:
        item1 = items["item1"]["value"]
        item2 = items["item2"]["value"]
        entity = items["entity"]["value"]

        if not entity_item_dict.get(entity):
            entity_item_dict[entity] = [item1, item2]
        else:
            set_items = entity_item_dict.get(entity)
            if item1 not in set_items:
                entity_item_dict[entity].append(item1)
            if item2 not in set_items:
                entity_item_dict[entity].append(item2)

    return entity_item_dict

###


def graph_constructor():
    # For each entity and the list containing items related to that entity
    for key_entity, item_list_value in make_entity_item_dict().items():

        #print("-- Item --")
        # Make a list to store the output from item_lifter when applied to each item related to an entity
        item_list = []

        #print("Key:", key_entity, "value:", item_list_value)

        # For each item in the list of items related to an entity, apply the item_lifter function
        for item in item_list_value:
            item_output = item_lifter(item)
            item_list.append(item_output)

        # Initialises the lists which are to hold the values related to an entity
        time_list, irl_list, anchor_list, annotator_list, collection_list, text_list = ([] for i in range(6))

        # Takes the different value properties and adds them in separate lists
        for item in item_list:
            time_list.append(item["time"]["value"])
            irl_list.append(item["irl"]["value"])
            anchor_list.append(item["anchor"]["value"])
            collection_list.append(item["collection"]["value"])
            text_list.append(item["text"]["value"])

        #print(time_list)
        #print(irl_list)
        #print(anchor_list)
        #print(collection_list)
        #print(text_list)

        # ------------------- Make Event graph -------------------

        # Make graph
        g = Graph()

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

        event_hash_value = uuid_generator.generate_uuid()

        Event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)

        # Event hash
        g.add((Event, RDF.type, nhterm.Event))

        # nhterm:DescribedBy
        for item in item_list_value:
            g.add((Event, nhterm.describedBy, URIRef(item)))

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
        for collec in collection_list:
            g.add((bn2, nhterm.hasDescriber, URIRef(collec)))

        # nhterm:hasEntity
        #g.add((bn2, nhterm.hasEntity, URIRef(entity)))

        # nhterm:sourceIRL
        for irl in irl_list:
            g.add((bn2, nhterm.sourceIRL, URIRef(irl)))

        # SourceDateTime
        for time in time_list:
            g.add((bn2, nhterm.sourceDateTime, URIRef(time)))

        # originalText
        #for text in text_list:
         #   g.add((bn2, nhterm.OriginalText, Literal(text, datatype=XSD.string)))

        #print(g.serialize(format="ttl").decode("utf-8"))


if __name__ == '__main__':
    graph_constructor()

# java -server -Xmx4g -jar blazegraph.jar