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
# variableAnnotation = (ex. anchorOf)


sparql.setQuery("""
PREFIX nhterm: <https://newshunter.uib.no/term#>
SELECT DISTINCT ?item1 ?item2 WHERE {
  
    ?item1 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation1 .
    ?superAnnotation1 nhterm:anchorOf ?anc .
    
    ?item2 a nhterm:Item ;
    nhterm:hasAnnotation ?superAnnotation2 . 
    ?superAnnotation2 nhterm:anchorOf ?anc . 
    
    FILTER(?item1 != ?item2)
	FILTER(STR(?anc) = "Trump")
    }	
    
    LIMIT 50
""")

sparql.setReturnFormat(JSON)
res = sparql.query().convert()

#for result in res["results"]["bindings"]:
 #   print(result)
    

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

# -----------------SourceDateTime----------
sparql.setQuery("""
    PREFIX nhterm: https://newshunter.uib.no/term#
    SELECT ?s ?p ?o
    WHERE
    {
       ?s a nhterm:Item .
        nhterm:sourceDateTime ?o .
    }
""")
sparql.setReturnFormat(JSON)
#sourceDateTime = sparql.query().convert()

#for result in sourceDateTime["results"]["bindings"]:
 #   print(result)

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
      """%item)
    sparql.setReturnFormat(RDFXML)

    res = sparql.queryAndConvert()
    graph_str = res.serialize(format="ttl").decode("utf-8")
    print(graph_str)

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
g = Graph()
g.parse(data=graph_str, format="ttl")


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


# java -server -Xmx4g -jar blazegraph.jar