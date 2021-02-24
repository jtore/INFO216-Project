from rdflib import Graph, Namespace

import owlrl

g = Graph()
g=g.parse(location="dataset_36.txt", format="turtle")

ex = Namespace("http://example.org/")
g.bind("ex",ex)

rdfs = owlrl.RDFSClosure.RDFS_Semantics(g,False, False, False)
rdfs.closure()
rdfs.flush_stored_triples()

