from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

import owlrl

"""
g = Graph()


# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource")
g.bind("nh", nh)

nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)

bn = BNode()

wikidata_dbpedia = URIRef("https://www.wikidata.org/wiki/Q276902")
dbpedia = URIRef("http://dbpedia.org/resource/")
newshunter_resource = ("https://newshunter.uib.no/resource/unresolved#")



def build_graph():

    #print("Program start, please select search condition:")

    anchorof_value = "Tesla" #input("Input anchorOf value for your graph: ")
    hasentity_value = "Nikola_Tesla" #input("Input entity value of graph: ")

    # Item
    #g.add((nh.ID, RDF.type, nhterm.Item))
    #g.add((nh.ID, nhterm.sourceDateTime, Literal("0001-01-01T00:00:00+00:00", datatype=XSD.dateTime)))

    # Annotation
    g.add((nhterm.hasAnnotation, RDF.type, bn))
    g.add((bn, RDF.type, nhterm.Annotation))
    g.add((bn, nhterm.anchorOf, Literal(anchorof_value, datatype=XSD.string)))
    g.add((bn, nhterm.hasAnnotator, wikidata_dbpedia))
    g.add((bn, nhterm.hasEntity, dbpedia + hasentity_value))

    # Contributor
    #g.add(())


    # if search_option == "a":
      #  search_anchorof = str(input("Input the anchor you want to search for (string values only): "))
    # if search_option == "an":
       # search_anotator = input("Input the resource for the annotator you want to search for. Format: (<https://yourresource.domain/>): ")
    # if search_option == "en":
     #   search_entity = input("Input the resource for the enitity you want to search for. Format: (<http://yourresource.domain/>)")

    print(g.serialize(format="ttl").decode("utf-8"))

build_graph()
"""


# Queries!

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.


sparql = SPARQLWrapper("http://192.168.0.76:9999/blazegraph/sparql")


# Query for å hente ut DateTime
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:sourceDateTime ?c
       
    }
""")

sparql.setReturnFormat(JSON)
DateTime = sparql.query().convert()

#for result in DateTime["results"]["bindings"]:
    #print(result["b"]["value"], "knows", result["c"]["value"])


# Query for alle tripler
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    
    SELECT ?subject ?predicate ?object
    WHERE {?subject ?predicate ?object}
    """)

sparql.setReturnFormat(JSON)
all_triples = sparql.query().convert()

#for result in all_triples["results"]["bindings"]:
 #   print(result["subject"]["value"], result["predicate"]["value"], result["object"]["value"])


sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
        ?b
        nhterm:sourceIRL ?c
    }
    LIMIT 10
""")

sparql.setReturnFormat(JSON)
sourceIRL = sparql.query().convert()

#for result in sourceIRL["results"]["bindings"]:
 #   print(result["b"]["value"], result["c"]["value"])


#for result in value["results"]["bindings"]:
 #   print(result)

# Query for å finne et nhterm:Item basert på en verdi i anchorOf inne i det itemet.

anchorof_value = "Tesla"

sparql.setQuery(
    """
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?item ?annotation WHERE {
        ?item nhterm:hasAnnotation ?annotation .
        ?annotation nhterm:anchorOf ?anchorvalue .
        
        FILTER(STR(?anchorvalue) = "%s")
    }
    """
%anchorof_value)

sparql.setReturnFormat(JSON)
test = sparql.query().convert()
for result in test["results"]["bindings"]:
    print(result["item"]["value"])


# Funker ikke, men er en begynnelse

'''
for result in test["results"]["bindings"]:
    res = result["item"]["value"]
    sparql.setQuery(
        """
        PREFIX nhterm: <https://newshunter.uib.no/term#>
        SELECT nhterm:hasAnnotation WHERE {
            ?item nhterm:hasAnnotation ?annotation .
            FILTER(STR(?item) = "%s")
        }
        """
        %res)
    sparql.setReturnFormat(JSON)
    test2 = sparql.query().convert()

    for result2 in test2["results"]["bindings"]:
        print(result2["results"]["item"])
'''
