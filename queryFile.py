from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL


import owlrl

nh = Namespace("https://newshunter.uib.no/resource")
nhterm = Namespace("https://newshunter.uib.no/term#")

print("Program start, please select search condition:")


def program_init(search_option,):

    if search_option == "a":
        search_anchorof = str(input("Input the anchor you want to search for (string values only): "))
    if search_option == "an":
        search_anotator = input("Input the resource for the annotator you want to search for. Format: (<https://yourresource.domain/>): ")
    if search_option == "en":
        search_entity = input("Input the resource for the enitity you want to search for. Format: (<http://yourresource.domain/>)")


g = Graph()

g.add((nhterm.hasAnnotation, RDF.type, nhterm.Annotation))

print(g.serialize(format="ttl").decode("utf-8"))


from SPARQLWrapper import SPARQLWrapper, JSON

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




