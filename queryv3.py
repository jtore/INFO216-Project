from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import owlrl

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")

# java -server -Xmx4g -jar blazegraph.jar

#anchorof_value = input("Input anchorOf value for your graph: ")

#-------------Queries------------#
# superAnnotation = a nhterm:Annotation
# p1 = nhterm: variable annotation (ex. anchorOf)
# o1 = verdien inne i annotation


sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
SELECT ?item1 ?item2 WHERE {
  
    ?item1 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation1 ;
    ?variableAnnotation1 ?valueOfAnnotation1 .
    ?superAnnotation1 nhterm:anchorOf ?anc . 
    
    ?item2 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation2 ;
    ?variableAnnotation2 ?valueOfAnnotation2 .
    ?superAnnotation2 nhterm:anchorOf ?anc . 
    
    ?annotation1 ?ap1 ?ao1 .
    ?annotation2 ?ap2 ?ao2 .
    FILTER(?item1 != ?item2)
    FILTER(STR(?anc) = "Trump")
    }	
    LIMIT 50
""")

'''
sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
SELECT * WHERE {
    ?item1 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation1 ;
    ?variableAnnotation1 ?valueOfAnnotation1 .
    ?superAnnotation1 nhterm:hasEntity ?entity .
    
    ?item2 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation2 ;
    ?variableAnnotation2 ?valueOfAnnotation2 .
    ?superAnnotation2 nhterm:hasEntity ?entity .
    
    ?annotation1 ?ap1 ?ao1 .
    ?annotation2 ?ap2 ?ao2 .
    }
    LIMIT 10
""")
'''

sparql.setReturnFormat(JSON)
res = sparql.query().convert()

for result in res["results"]["bindings"]:
    print(result)
    

#-----------------AnchorOf----------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?anc
    WHERE
    {
       ?pred
       nhterm:anchorOf ?anc

    }
""")
sparql.setReturnFormat(JSON)
anchorOf = sparql.query().convert()

#-----------------hasAnnotator----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?hasann
    WHERE
    {
       ?pred
       nhterm:hasAnnotator ?hasann
    
    }
    LIMIT 1
""")
sparql.setReturnFormat(JSON)
hasAnnotator = sparql.query().convert()


#-----------------hasEntity----------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?hasent
    WHERE
    {
       ?pred
       nhterm:hasEntity ?hasent

    }
""")
sparql.setReturnFormat(JSON)
hasEntity = sparql.query().convert()

#-----------------hasContributor----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?hascont
    WHERE
    {
       ?pred
       nhterm:hasContributor ?hascont

    }
""")
sparql.setReturnFormat(JSON)
hasContributor = sparql.query().convert()


#-----------------inCollection----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?incol
    WHERE
    {
       ?pred
       nhterm:inCollection ?incol

    }
""")
sparql.setReturnFormat(JSON)
inCollection = sparql.query().convert()


#------------------originalText--------------

sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?pred ?orig
    WHERE
    {
        ?pred
        nhterm:originalText ?orig
    }
    
""")

sparql.setReturnFormat(JSON)
originalText = sparql.query().convert()

#-----------------SourceDateTime----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?b ?c ?g
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
    SELECT  ?sub ?pred ?irl
    WHERE
    {
        ?sub
        ?irl
        ?pred
        FILTER(?irl != nhterm:sourceIRL)
    }
""")

sparql.setReturnFormat(JSON)
sourceIRL = sparql.query().convert()



# ----- AnchorOf Query ------

# Query for å finne et nhterm:Item basert på en verdi i anchorOf inne i det itemet.

anchorof_value = "Tesla"

sparql.setQuery(
    """
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?item WHERE {
        ?item nhterm:hasAnnotation ?annotation .
        ?annotation nhterm:anchorOf ?anchorvalue .
        FILTER(STR(?anchorvalue) = "%s")
    }
    """
%anchorof_value)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
#for result in results["results"]["bindings"]:
 #   return_value = result["item"]["value"]



# ---------- DESCRIBE QUERY ----------

sparql.setQuery("""
       DESCRIBE ?item WHERE{
          ?item ?annotation ?annotation
          FILTER(STR(?item) = "%s")
       }
  """)
sparql.setReturnFormat(RDFXML)

res = sparql.queryAndConvert()
graph_str = res.serialize(format="ttl").decode("utf-8")

#g = Graph()
#g.parse(data=graph_str, format="ttl")
#print(graph_str)

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
 #   g.add((URIRef(result["sub"]["value"]), nhterm.sourceIRL, Literal(result["pred"]["value"])))

print(g.serialize(format="ttl").decode("utf-8"))

# java -server -Xmx4g -jar blazegraph.jar