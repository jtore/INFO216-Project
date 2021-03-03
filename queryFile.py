from rdflib import Graph, Namespace

import owlrl

g = Graph()
g=g.parse(location="dataset_36.txt", format="turtle")

nh = Namespace("https://newshunter.uib.no/resource#")
nhterm = Namespace("https://newshunter.uib.no/term#")


g.bind("nh", nh)
g.bind("nhterm", nhterm)


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
    SELECT ?b ?c
    WHERE
    {
       nh:040f153c-136e-4dbe-99c7-7cde19e27c6b ?b ?c;
       nhterm:sourceDateTime ?c

    }
""")



for row in ann:
    print("%s knows %s" % row)


rdfs = owlrl.RDFSClosure.RDFS_Semantics(g, False, False, False)
rdfs.closure()
rdfs.flush_stored_triples()





