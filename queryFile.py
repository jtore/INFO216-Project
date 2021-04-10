from rdflib import Graph, Namespace

import owlrl

from SPARQLWrapper import SPARQLWrapper, JSON

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")


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

for result in sourceIRL["results"]["bindings"]:
    print(result["b"]["value"], result["c"]["value"])




