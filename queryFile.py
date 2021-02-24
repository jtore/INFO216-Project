from rdflib import Graph, Namespace

import owlrl

g = Graph()
g=g.parse(location="dataset_36.txt", format="turtle")

nh = Namespace("https://newshunter.uib.no/resource#")
##nhterm = Namespace("https://newshunter.uib.no/term#")


g.bind("nh", nh)
##g.bind("nhterm", nhterm)

rdfs = owlrl.RDFSClosure.RDFS_Semantics(g, False, False, False)
rdfs.closure()
rdfs.flush_stored_triples()

ann = g.query("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    ASK{
        nh:11febd8d-7d7e-4efd-8d47-0353286790e6 nhterm:Item nhterm:hasAnnotation; 
    }
""")

print(bool(ann))



