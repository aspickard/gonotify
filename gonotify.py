#!/usr/bin/python

import requests
import sys
import random
import sys

HEADERS = {
    'cache-control': 'no-cache',
    'origin': 'https://fastpokemap.se',
    'pragma': "no-cache",
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36',
}

def requestMons(lat, lng, headers=HEADERS, max_tries=100):
    # Becomes True after a successful response has been gathered
    success = False
    # Act like we are firefox
    # Location parameters to query
    location = {
        'lat': lat,
        'lng': lng
    }
    headers=headers
    # How many tries have been made since a successful response
    tries = 0
    response = {}
    new_encounters = []
    new_lures = []

    # Keep requesting until successful or exceed max_tries
    while not success and tries < max_tries:
        response = requests.get("https://api.fastpokemap.se", params=location, headers=HEADERS)
        try:
            response = response.json()
            # We get this when the server is overloaded
            if 'error' in response:
                tries+=1
            else:
                success = True

            if success:
                for encounter in response['result']:
                    if 'lure_info' in encounter and encounter['lure_info']['encounter_id']:
                        new_lures.append(encounter['lure_info'])
                    elif 'spawn_point_id' in encounter:
                        new_encounters.append(encounter)

        # Handle other (likely 5XX) errors.
        except:
            tries += 1

    return {"lures":new_lures, "encounters":new_encounters, "success":success, "tries":tries}

