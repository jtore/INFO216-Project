from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import owlrl

from SPARQLWrapper import SPARQLWrapper, JSON

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")

#anchorof_value = input("Input anchorOf value for your graph: ")

#-------------Queries------------#

#-----------------AnchorOf----------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:anchorOf ?c

    }
""")
sparql.setReturnFormat(JSON)
anchorOf = sparql.query().convert()

#-----------------hasAnnotator----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:hasAnnotator ?c
    
    }
    LIMIT 1
""")
sparql.setReturnFormat(JSON)
hasAnnotator = sparql.query().convert()


#-----------------hasEntity----------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:hasEntity ?c

    }
""")
sparql.setReturnFormat(JSON)
hasEntity = sparql.query().convert()

#-----------------hasContributor----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:hasContributor ?c

    }
""")
sparql.setReturnFormat(JSON)
hasContributor = sparql.query().convert()

# -----------------originalText----------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:originalText ?c

    }
""")
sparql.setReturnFormat(JSON)
originalText = sparql.query().convert()
#-----------------inCollection----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       nhterm:inCollection ?c

    }
""")
sparql.setReturnFormat(JSON)
inCollection = sparql.query().convert()


#------------------originalText--------------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
        ?b
        nhterm:originalText ?c
    }
    
""")

sparql.setReturnFormat(JSON)
originalText = sparql.query().convert()

#-----------------SourceDateTime----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       ?b
       ?g ?c
       FILTER(?g != %s)

    }
""" %"nhterm:sourceDateTime")
sparql.setReturnFormat(JSON)
sourceDateTime = sparql.query().convert()

#------------------SourceIRL--------------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT  ?b ?c ?g
    WHERE
    {
        ?b
        ?g
        ?c
        FILTER(?g != nhterm:sourceIRL)
    }
""")

sparql.setReturnFormat(JSON)
sourceIRL = sparql.query().convert()

#------------------Graph-------------------


g = Graph()
# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource")
g.bind("nh", nh)
nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)
bn = BNode()

#-------------------------Results---------------------------------#


#for result in sourceIRL["results"]["bindings"]:
  #  print(result["b"]["value"], result["c"]["value"])

for result in sourceIRL["results"]["bindings"]:
    g.add((URIRef(result["b"]["value"]),nhterm.sourceIRL, URIRef(result["c"]["value"])))

print(g.serialize(format="ttl").decode("utf-8"))



#for result in all_triples["results"]["bindings"]:    print(result["predicate"]["value"], result["object"]["value"])

#for result in all_triples["results"]["bindings"]:
#    print(result["object"]["value"])