#!/usr/bin/env python3

import sys
import io
import csv
import getopt
import urllib.request
import prettytable
import RDF

def main(argv):
    endpoint = None
    modelFile = None
    query = None

    try:
        opts, args = getopt.getopt(argv, "e:q:f:", ["endpoint", "file", "query"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-e", "--endpoint"):
            endpoint = a
        elif o in ("-f", "--file"):
            modelFile = a
        elif o in ("-q", "--query"):
            query = a

    if query is None:
        # TODO alternatively read query from stdin or provide editor to enter it at runtime
        raise Exception('No query string was given')

    # decide which method to use
    # TODO if both params are given print a warning
    if not modelFile is None:
        modelFile = 'file:' + modelFile
        localEvaluation(modelFile, query)
    elif not endpoint is None:
        onlineRequest(endpoint, query)
    else:
        # TODO alternatively read rdf from stdin
        raise Exception('No endpoint or model file was given')

def onlineRequest(endpoint, query):
    userAgent = 'SPARQL.sh 0.0.1-pre'
    rdfMimeTypes="text/turtle; q=1.0, application/x-turtle; q=0.9, text/n3; q=0.8, application/rdf+xml; q=0.5, text/plain; q=0.1"
    #sparqlMimeTypes="application/sparql-results+json; 1=1.0, application/sparql-results+xml; q=0.9, text/csv; q=0.5, text/tab-separated-values; q=0.4"
    sparqlMimeTypes="text/csv; q=1.0, text/tab-separated-values; q=0.5, text/plain; q=0.1"

    requestHeaders = { 'User-Agent': userAgent, 'Accept': sparqlMimeTypes, 'Accept-Charset': 'UTF-8' }
    requestValues = {'query': query}

    requestData = urllib.parse.urlencode(requestValues)
    requestData = requestData.encode('utf-8')

    request = urllib.request.Request(endpoint, requestData, requestHeaders)
    try:
        response = urllib.request.urlopen(request)
        result = readResult(response)
        printResult(result)

    except urllib.error.HTTPError as e:
        print(e.reason)
        errorBody = e.read()
    except urllib.error.URLError as e:
        print(e.reason)

def localEvaluation(modelSourceUri, queryString):
    model = RDF.Model()
    # TODO add possibility to explicitely set the content type and register things like namespaces = ttlParser.namespaces_seen()
    model.load(modelSourceUri)
    query = RDF.SPARQLQuery(queryString)
    result = query.execute(model)
    printQueryResults(result)

class MyDialect(csv.Dialect):
    strict = True
    skipinitialspace = True
    quoting = csv.QUOTE_ALL
    delimiter = ','
    quotechar = '"'
    lineterminator = '\n'

def readResult(response):
    responseHeader = response.info()
    # TODO check the content type to switch between parsers
    mimeType = responseHeader['Content-Type'].split(';')[0]
    encoding = responseHeader['Content-Type'].split(';')[1].split('=')[1]

    if (mimeType != 'text/csv' and mimeType != 'text/tab-separated-values' and mimeType != 'text/plain'):
        print('Sorry, mime/type of answer it currently unsupported:', mimeType)
        return
    responseString = response.read().decode(encoding)
    resultSet = csv.reader(io.StringIO(responseString))
    return resultSet

def printResult(resultSet):
    header = next(resultSet, None)
    resultsTable = prettytable.PrettyTable(header)
    for row in resultSet:
        resultsTable.add_row(row)
    print(resultsTable)

def printQueryResults(resultsObject):
    #print(result)
    cols = resultsObject.get_bindings_count()
    header = []
    for i in range(cols):
        header.append(resultsObject.get_binding_name(i))
    resultsTable = prettytable.PrettyTable(header)
    for result in resultsObject:
        row = []
        for i in range(cols):
            row.append(str(result[header[i]]))
        resultsTable.add_row(row)
    print(resultsTable)

def usage():
    print("Please use -e and -q")

if __name__ == "__main__":
        main(sys.argv[1:])
