from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL
import owlrl

from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML

# This creates a server connection to the same URL that contains the graphic interface for Blazegraph.
# You also need to add "sparql" to end of the URL like below.

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")

#anchorof_value = input("Input anchorOf value for your graph: ")

# -------------Queries------------#

sparql.setQuery("""

PREFIX nhterm: <https://newshunter.uib.no/term#>
SELECT DISTINCT ?item1 ?item2 WHERE {

    ?item1 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation1 .
    ?superAnnotation1 nhterm:anchorOf "Tesla" . 

    ?item2 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation2 .
    ?superAnnotation2 nhterm:anchorOf "Tesla" . 
    
    }

    LIMIT 50
""")

sparql.setReturnFormat(JSON)
test = sparql.query().convert()

# -----------------SourceDateTime----------
sparql.setQuery("""
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?s ?p ?o
    WHERE
    {
        ?s a nhterm:Item ;
        nhterm:sourceDateTime ?o .
    }
""")
sparql.setReturnFormat(JSON)
sourceDateTime = sparql.query().convert()


g = Graph()
# Bind prefix and namespace
nh = Namespace("https://newshunter.uib.no/resource")
g.bind("nh", nh)
nhterm = Namespace("https://newshunter.uib.no/term#")
g.bind("nhterm", nhterm)
bn = BNode()

sparql.setQuery("""

    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX nhterm: <https://newshunter.uib.no/term#>
    SELECT ?item ?dt ?year ?month ?day ?hours ?minutes 
    WHERE
    {
          ?item a nhterm:Item ;
        nhterm:sourceDateTime ?dt
        bind(year(?dt) as ?year)
        bind(month(?dt) as ?month)
        bind(day(?dt) as ?day)
        bind(hours(?dt) as ?hours)
        bind(minutes(?dt) as ?minutes)
    }
        ORDER BY ?year ?month ?day ?hours ?minutes
        LIMIT 1


""")

time_results = sparql.query().convert()
for result in time_results["results"]["bindings"]:
    item = result["item"]["value"]
    sparql.setQuery("""
           DESCRIBE ?item WHERE{
              ?item ?annotation ?annotation
              FILTER(STR(?item) = "%s")
           }
      """ % item)
    sparql.setReturnFormat(RDFXML)

    res = sparql.queryAndConvert()
    graph_str = res.serialize(format="ttl").decode("utf-8")
    print(graph_str)

# Starte Blazegraph server:  java -server -Xmx4g -jar blazegraph.jar