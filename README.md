SPARQL.sh
=========
SPARQL client to be used on the terminal

Usage
-----

    sparql -e 'http://dbpedia.org/sparql' -q 'select ?r { ?r a <http://dbpedia.org/ontology/Place> } limit 5'

Requirements
------------

    * python >=3
    * python3-prettytable
    * [python3-librdf](http://librdf.org/docs/python.html) (redland librdf bindings for python 3) https://github.com/dajobe/redland-bindings
