from rdflib import Graph, Namespace

import owlrl

# Lager grafen
g = Graph()

# Parse grafen og laste den inn i g
g=g.parse(location="dataset_36.ttl", format="turtle")

# Lage namespace
nh = Namespace("https://newshunter.uib.no/resource#")
nhterm = Namespace("https://newshunter.uib.no/term#")

# Binder namespace
g.bind("nh", nh)
g.bind("nhterm", nhterm)

# Query for å hente ut DateTime
DateTime = g.query("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c
    WHERE
    {
       nh:040f153c-136e-4dbe-99c7-7cde19e27c6b ?b ?c;
       nhterm:sourceDateTime ?c
       
    }
""")

ann = g.query("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?subject ?predicate ?object
    WHERE {?subject ?predicate ?object} 
    LIMIT 10
""")


for row in DateTime:
    print("%s knows %s" % row)

#for row in ann:
 #   print("%s knows %s" % row)

rdfs = owlrl.RDFSClosure.RDFS_Semantics(g, False, False, False)
rdfs.closure()
rdfs.flush_stored_triples()





