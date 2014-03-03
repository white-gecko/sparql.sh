#!/usr/bin/env python3

import sys
import io
import csv
import getopt
import urllib.request
import prettytable

def main(argv):
    userAgent = 'SPARQL.sh 0.0.1'
    rdfMimeTypes="text/turtle; q=1.0, application/x-turtle; q=0.9, text/n3; q=0.8, application/rdf+xml; q=0.5, text/plain; q=0.1"
    #sparqlMimeTypes="application/sparql-results+json; 1=1.0, application/sparql-results+xml; q=0.9, text/csv; q=0.5, text/tab-separated-values; q=0.4"
    sparqlMimeTypes="text/csv; q=1.0, text/tab-separated-values; q=0.5"

    try:
        opts, args = getopt.getopt(argv, "e:q:", ["endpoint", "query"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-e", "--endpoint"):
            endpoint = a
        elif o in ("-q", "--query"):
            query = a

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
    encoding = responseHeader['Content-Type'].split(';')[1].split('=')[1]
    responseString = response.read().decode(encoding)
    #print(responseString)
    resultSet = csv.reader(io.StringIO(responseString))
    return resultSet

def printResult(resultSet):
    header = next(resultSet, None)
    results = prettytable.PrettyTable(header)
    for row in resultSet:
        results.add_row(row)
    print(results)

def usage():
    print("Please use -e and -q")

if __name__ == "__main__":
        main(sys.argv[1:])
