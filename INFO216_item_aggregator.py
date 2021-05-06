from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import uuid_generator

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
sparql = SPARQLWrapper("http://sandbox.i2s.uib.no/bigdata/sparql")


"""-------------------Item lifter function-------------------"""


# Explained in the report
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
    # Returns the query result in JSON format
    sparql.setReturnFormat(JSON)

    # Converts the result
    return_block = sparql.query().convert()
    # We return the result for each item invoked with the function
    for result in return_block["results"]["bindings"]:
        return result


"""------------------- Making the dictionaries for values -------------------"""
# Explained in the report


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

    # Dictionaries for lists of items, anchors and annotator to be used later
    entity_item_dict = {}
    entity_anchor_dict = {}
    entity_annotator_dict = {}

    # For each item in the entity_graph produced by the above query
    for items in entity_graph["results"]["bindings"]:
        # Here we assign each result to a variable so that we can make pairs later
        item1 = items["item1"]["value"]
        item2 = items["item2"]["value"]
        entity = items["entity"]["value"]
        anchor1 = items["anchor1"]["value"]
        anchor2 = items["anchor2"]["value"]
        annotator1 = items["annotator1"]["value"]
        annotator2 = items["annotator2"]["value"]

        # If entity does not exist as a key in the entity_item_dict
        if not entity_item_dict.get(entity):
            # Add the current entity as the key, and add the related items as a list of values
            entity_item_dict[entity] = [item1, item2]
            # Add the current entity into a new dictionary and pairs of corresponding anchors as value pairs
            entity_anchor_dict[entity] = [anchor1, anchor2]
            # Add the current entity into a new dictionary and pairs of corresponding annotator as value pairs
            entity_annotator_dict[entity] = [annotator1, annotator2]

        else:
            # If the entity does exist in the entity_item_dict
            # Get all items, anchors and annotators for an entity
            check_items = entity_item_dict.get(entity)
            check_anchor = entity_anchor_dict.get(entity)
            # Even though all items have one in the current dataset has annotator,
            # they might have two so we want to check for that aswell
            check_annotator = entity_annotator_dict.get(entity)

            # For our current set of items in entity_graph:
            # If the first item in our pair is not in the list of items related to the entity
            if item1 not in check_items:
                # Append the item related to the entity into the list of items
                entity_item_dict[entity].append(item1)

            # Same as for item1, but for the second item in the comparison
            if item2 not in check_items:
                entity_item_dict[entity].append(item2)

            # If the first anchor value in our anchor pairs is not already in the dictionary
            if anchor1 not in check_anchor:
                # Add the anchor to the value list in the dictionary
                entity_anchor_dict[entity].append(anchor1)

            # Same as for anchor1, but for the second anchor in the value-pair
            if anchor2 not in check_anchor:
                entity_anchor_dict[entity].append(anchor2)

            # If the first annotator value is not in the dictionary containing annotators for our entity
            if annotator1 not in check_annotator:
                entity_annotator_dict[entity].append(annotator1)

            # Same as for annotator1, but for the second annotator
            if annotator2 not in check_annotator:
                entity_annotator_dict[entity].append(annotator2)

    # Return the dictionaries for (entity: item_list), (entity:anchor_list) and (entity, annotator)
    return entity_item_dict, entity_anchor_dict, entity_annotator_dict


"""------------------- Constructing the graph -------------------"""


def graph_constructor():

    # For each entity and the list containing items related to that entity
    for key_entity, item_list_value in make_entity_item_dict()[0].items():

        # Make a list to store the output from item_lifter when applied to each item related to an entity
        item_list = []

        # For each item in the list of items related to an entity, apply the item_lifter function
        for item in item_list_value:
            item_output = item_lifter(item)
            item_list.append(item_output)

        # Initialises the lists which are to hold the values related to an entity
        datetime_list, sourceirl_list, incollection_list, originaltext_list = ([] for i in range(4))

        # Takes the different entity properties and adds them in separate lists
        for item in item_list:
            # DateTime for each item related to the entity
            datetime_list.append(item["time"]["value"])
            # SourceIRL for each item related to the entity
            sourceirl_list.append(item["irl"]["value"])
            # InCollection for each item related to the entity
            incollection_list.append(item["collection"]["value"])
            # OriginalText for each item related to the entity
            originaltext_list.append(item["text"]["value"])

        # Gets all the anchorOf values for the specific entity and removes duplicates if they exist
        anchor_list = list(set(make_entity_item_dict()[1].get(key_entity)))

        # The same as above but for the list of annotations for a specific entity
        annotator_list = list(set(make_entity_item_dict()[2].get(key_entity)))

        """-------------------Adding to the graph-------------------"""
        # Make empty graph
        g = Graph()

        # Bind prefixes and namespaces to use
        # nh
        nh = Namespace("https://newshunter.uib.no/resource#")
        g.bind("nh", nh)

        # nhterm
        nhterm = Namespace("https://newshunter.uib.no/term#")
        g.bind("nhterm", nhterm)

        # Blank node
        bn = BNode()

        # uuid for nhterm:Event
        event_hash_value = uuid_generator.generate_uuid()
        event = URIRef("https://newshunter.uib.no/resource#" + event_hash_value)

        # nhterm:Event
        g.add((event, RDF.type, nhterm.Event))

        # nhterm:DescribedBy
        for item in item_list_value:
            g.add((event, nhterm.describedBy, URIRef(item)))

        # nhterm:Descriptor
        g.add((event, nhterm.hasDescriptor, bn))
        g.add((bn, RDF.type, nhterm.Descriptor))

        # ntherm:anchorOf
        for anchor_list in anchor_list:
            g.add((bn, nhterm.anchorOf, Literal(anchor_list, datatype=XSD.string)))

        # nhterm:hasDescriber
        for annotator in annotator_list:
            g.add((bn, nhterm.hasDescriber, URIRef(annotator)))

        # nhterm:hasDescriber
        for collec in incollection_list:
           g.add((bn, nhterm.inCollection, URIRef(collec)))

        # nhterm:hasEntity
        g.add((bn, nhterm.hasEntity, URIRef(key_entity)))

        # nhterm:sourceIRL
        for irl in sourceirl_list:
            g.add((bn, nhterm.sourceIRL, URIRef(irl)))

        # SourceDateTime
        for time in datetime_list:
            g.add((bn, nhterm.sourceDateTime, URIRef(time)))

        # originalText
        for text in originaltext_list:
            g.add((bn, nhterm.OriginalText, Literal(text, datatype=XSD.string)))

        # serializes and prints the event graphs, one by one
        print(g.serialize(format="ttl").decode("utf-8"))


if __name__ == '__main__':
    graph_constructor()

