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
        SELECT ?time ?text ?irl ?contributor ?collection
            WHERE
            {
            ?item a nhterm:Item ;
                nhterm:originalText ?text ;
                nhterm:sourceDateTime ?time ;
                nhterm:sourceIRL ?irl ;
                nhterm:hasContributor ?contributor ;
                nhterm:inCollection ?collection ;

            FILTER(STR(?item) ="%s")
            }
            """ % external_item)
    sparql.setReturnFormat(JSON)

    return_block = sparql.query().convert()
    for result in return_block["results"]["bindings"]:
        return result


def make_entity_item_dict():
    sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
        SELECT DISTINCT ?item1 ?item2 ?entity ?anchor1 ?anchor2 ?annotator1 ?annotator2 WHERE {

            ?item1 a nhterm:Item ;
            nhterm:hasAnnotation ?superAnnotation1 .
            ?superAnnotation1 nhterm:hasEntity ?entity .
            ?superAnnotation1 nhterm:anchorOf ?anchor1 .
            ?superAnnotation1 nhterm:hasAnnotator ?annotator1 . 

            ?item2 a nhterm:Item ;
            nhterm:hasAnnotation ?superAnnotation2 .
            ?superAnnotation2 nhterm:hasEntity ?entity . 
            ?superAnnotation2 nhterm:anchorOf ?anchor2 .
            ?superAnnotation2 nhterm:hasAnnotator ?annotator2 .
            FILTER(?item1 != ?item2)
        }
    """)
    sparql.setReturnFormat(JSON)
    entity_graph = sparql.query().convert()

    entity_item_dict = {}
    entity_anchor_dict = {}
    entity_annotator_dict = {}

    for items in entity_graph["results"]["bindings"]:
        item1 = items["item1"]["value"]
        item2 = items["item2"]["value"]
        entity = items["entity"]["value"]
        anchor1 = items["anchor1"]["value"]
        anchor2 = items["anchor2"]["value"]
        annotator1 = items["annotator1"]["value"]
        annotator2 = items["annotator2"]["value"]

        # print(anchor1, anchor2, annotator1, annotator2)

        # If entity does not exist as a key in the entity_item_dict
        if not entity_item_dict.get(entity):
            # Add the current entity as the key, and add the related items as a list of values
            entity_item_dict[entity] = [item1, item2]
            entity_anchor_dict[entity] = [anchor1, anchor2]
            entity_annotator_dict[entity] = [annotator1, annotator2]
        else:
            # If the entity does exist in the entity_item_dict
            set_items = entity_item_dict.get(entity)
            check_anchor = entity_anchor_dict.get(entity)
            check_annotator = entity_annotator_dict.get(entity)

            # Append the next item related to the entity into the list of items
            if item1 not in set_items:
                entity_item_dict[entity].append(item1)

            if anchor1 not in check_anchor:
                if anchor2 != None:
                    entity_anchor_dict[entity].append(anchor1)

            if annotator1 not in check_annotator:
                entity_annotator_dict[entity].append(annotator1)

            # Same as above, but for the second item in the comparison
            if item2 not in set_items:
                entity_item_dict[entity].append(item2)

            if anchor2 not in check_anchor:
                if anchor2 != None:
                   entity_anchor_dict[entity].append(anchor2)

            if annotator2 not in check_annotator:
                entity_annotator_dict[entity].append(annotator2)

    return entity_item_dict, entity_anchor_dict, entity_annotator_dict


###


def graph_constructor():
    # For each entity and the list containing items related to that entity

    for key_entity, item_list_value in make_entity_item_dict()[0].items():

        # print("-- Item --")
        # Make a list to store the output from item_lifter when applied to each item related to an entity
        item_list = []

        # print("Key:", key_entity, "value:", item_list_value)

        # For each item in the list of items related to an entity, apply the item_lifter function
        for item in item_list_value:
            item_output = item_lifter(item)
            item_list.append(item_output)

        # Initialises the lists which are to hold the values related to an entity
        time_list, irl_list, collection_list, text_list = ([] for i in range(4))

        # Takes the different value properties and adds them in separate lists
        for item in item_list:
            time_list.append(item["time"]["value"])
            irl_list.append(item["irl"]["value"])
            collection_list.append(item["collection"]["value"])
            text_list.append(item["text"]["value"])

        print(make_entity_item_dict()[1].get(key_entity))
      #  print("If there is a entity, print it here:", key_entity, item_list_value)
        the_annotator = make_entity_item_dict()[2].get(key_entity)
        the_entity = make_entity_item_dict()[1].get(key_entity)

        anchor_list = []
        if the_entity != None:
            for i in the_entity:
                if i in anchor_list:
                    pass
                else:
                    anchor_list.append(i)

        annotator_list = []

        if the_annotator != None:
            for i in the_annotator:
                if i in annotator_list:
                    pass
                else:
                    annotator_list.append(i)
        print("annotator_list", annotator_list)





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

        # nhterm:Descriptor
        g.add((Event, nhterm.hasDescriptor, bn2))
        g.add((bn2, RDF.type, nhterm.Descriptor))


        #ntherm:anchorOf
        for anchor in anchor_list:
            g.add((bn2, nhterm.anchorOf, Literal(anchor, datatype=XSD.string)))

        # nhterm:hasDescriber
        for annotator in annotator_list:
            g.add((bn2, nhterm.hasDescriber, URIRef(annotator)))

        # nhterm:hasDescriber
        #for collec in collection_list:
         #   g.add((bn2, nhterm.hasDescriber, URIRef(collec)))

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

        print(g.serialize(format="ttl").decode("utf-8"))




if __name__ == '__main__':
    graph_constructor()

# java -server -Xmx4g -jar blazegraph.jar