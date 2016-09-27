import requests
import json
from sys import argv, exit
from time import sleep
from elasticsearch import Elasticsearch

if len(argv) > 1:
    WEBHOOK = argv[1]
else:
    print("Usage:")
    print("python goslack.py SLACK_WEBHOOK_URL [DELAY] [ELASTICSEARCH_HOST] [ELASTICSEARCH_PORT]")

# DELAY between elasticsearch queries in minutes
if len(argv) > 2:
    DELAY = int(argv[2])
else:
    DELAY = 1

# URL of the elasticsearch server
if len(argv) > 3:
    HOST = argv[3]
else:
    HOST = "http://localhost"

# Port of the elasticsearch server
if len(argv) > 4:
    PORT = int(argv[4])
else:
    PORT = 9200

client = Elasticsearch(hosts=[HOST], port=PORT)
QUERY = {"query":{"bool":{"must":[{"match_all":{}},{"range":{"encounter.discovery_time":{"gt":"now-{}m".format(DELAY),"to":"now"}}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"facets":{}}

while True:
    try:
        response = client.search(index="pogo_work", body=QUERY)
        for hit in response['hits']['hits']:
            mon = hit['_source']['pokemon_id']
            if mon == "NIDORAN_FEMALE":
                mon = "NIDORANF"
            elif mon == "NIDORAN_MALE":
                mon = "NIDORANM"
            mon_image = ":pokemon-{}:".format(mon)
            body = {"channel": "#poke_gym", "username": "Professor Oak", "text": "{} appeared near the office!".format(mon), "icon_emoji": mon_image}
            print(mon)
            response = requests.post(WEBHOOK, json.dumps(body), headers={'content-type': 'application/json'})
    except:
        print("Error querying elastic.")
    sleep(DELAY * 60 + 1)
