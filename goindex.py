import json
import subprocess
import sys
import elasticsearch
from elasticsearch import Elasticsearch
from datetime import datetime

from time import sleep
from gonotify import requestMons

LAT = sys.argv[1]
LONG = sys.argv[2]
LABEL = "pogo_" + sys.argv[3]
HOST = "http://localhost"
DELAY = 5

client = Elasticsearch(hosts=[HOST], port=9200)

if len(sys.argv) >= 5:
    DELAY = int(sys.argv[4])

if len(sys.argv) < 3:
    print "\nUsage: gonotify.py latitude longitude [delay]"
    print "latitude: latitude position to scan from."
    print "longitude: longitude position to scan from."
    print "label: if present, output to log file with this prefix and disable notifications.\n"
    print "delay (optional): delay in minutes after a successful scan.\n"
    sys.exit()

def sendmessage(message):
    subprocess.Popen(['notify-send', message])

def epochStringToDatetime(epoch):
    if int(epoch) > 0:
        expiration_time = int(epoch) / 1000
        expiration_time = datetime.utcfromtimestamp(expiration_time)
        return expiration_time
    else:
        return None

while True:
    results = requestMons(LAT, LONG)

    if results['success']:
        for encounter in results['encounters']:
            encounter['discovery_time'] = datetime.utcnow()
            encounter['expiration_time'] = epochStringToDatetime(encounter['expiration_timestamp_ms'])
            try:
                client.get(index=LABEL, id=encounter['encounter_id'])
            except elasticsearch.exceptions.NotFoundError as e:
                client.index(index=LABEL, doc_type="encounter", id=encounter['encounter_id'], body=encounter)

        for lure in results['lures']:
            lure['discovery_time'] = datetime.utcnow()
            lure['expiration_time'] = epochStringToDatetime(lure['lure_expires_timestamp_ms'])
            lure['pokemon_id'] = lure['active_pokemon_id']
            try:
                client.get(index=LABEL, id=lure['encounter_id'])
            except elasticsearch.exceptions.NotFoundError as e:
                client.index(index=LABEL, doc_type="lure", id=lure['encounter_id'], body=lure)

    sleep(DELAY*60)
