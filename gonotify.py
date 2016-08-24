#!/usr/bin/python

import requests
import subprocess
import sys
import random
from time import sleep
from datetime import datetime

if len(sys.argv) < 3:
    print "\nUsage: gonotify.py latitude longitude [delay]"
    print "latitude: latitude position to scan from."
    print "longitude: longitude position to scan from."
    print "delay (optional): delay in minutes after a successful scan.\n"
    sys.exit()

DELAY = 5
LAT = sys.argv[1]
LONG = sys.argv[2]

if len(sys.argv) == 4:
    DELAY = int(sys.argv[3])

print "Scanning ({},{}) every {} minutes.".format(LAT, LONG, DELAY)

def sendmessage(message):
    subprocess.Popen(['notify-send', message])

def printline():
    print "\n--------------------------------------------------------------"

# Encounters that have been seen already
cur_encounters = {}
# Nearby that have been seen already
cur_nearby = {}

# Loop until the user ends the application
while True:
    # Becomes True after a successful response has been gathered
    success = False
    # Act like we are firefox
    headers = {
        'cache-control': 'no-cache',
        'origin': 'https://fastpokemap.se',
        'pragma': "no-cache",
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36',
    }
    # Location parameters to query
    location = {
        'lat': LAT,
        'lng': LONG
    }
    # How many tries have been made since a successful response
    tries = 0

    # Keep requesting until successful
    while not success:
        print "Requesting... (attempt {0} at {1})".format(tries, datetime.now())
        response = requests.get("https://api.fastpokemap.se", params=location, headers=headers)
        try:
            response = response.json()
            # We get this when the server is overloaded
            if 'error' in response:
                tries+=1
            else:
                printline()
                print "\nSuccess! ({0})\n".format(datetime.now())
                # We have a valid response
                success = True
                # Will be set to true if we see a mon nearby that we've already seen before
                lingering_nearby = False
                # This will be the cur_encounters after the response is processed
                new_encounters = {}
                # Will populate with any new nearby mon
                new_nearby = {}
                # Will consolidate all nearby and lingering nearby into one message
                nearby_message = "Nearby: "
                lingering_nearby_message = "Lingering nearby: "
                # Iterate over each mon in result
                for encounter in response['result']:
                    # If we know the spawn point then it is an encounter we can see
                    # If not in cur_encounters then it is a new spawn
                    if encounter['encounter_id'] not in cur_encounters and 'spawn_point_id' in encounter:
                        new_encounters[encounter['encounter_id']] = encounter
                        # Response time is in ms
                        time_left = -((int(datetime.now().strftime('%s')) * 1000) - int(encounter['expiration_timestamp_ms'])) / 1000
                        minutes = time_left / 60
                        seconds = time_left % 60
                        seconds = "%02d" % seconds
                        message = "Encountered {id} - {min}:{sec} remains.".format(id=encounter["pokemon_id"], min=minutes, sec=seconds)
                        # Print to terminal
                        print message
                        # Show desktop alert
                        sendmessage(message)
                    # Otherwise it is a lingering spawn
                    elif 'spawn_point_id' in encounter:
                        new_encounters[encounter['encounter_id']] = encounter
                        # Print to terminal but no notification
                        message = "Lingering {id} - {min}:{sec} remains.".format(id=encounter["pokemon_id"], min=minutes, sec=seconds)
                        print message
                    # If we don't know the spawn point, then it is nearby
                    # If not in cur_nearby then it is a newly seen nearby mon
                    elif 'spawn_point_id' not in encounter and encounter['encounter_id'] not in cur_nearby:
                        new_nearby[encounter['encounter_id']] = encounter
                        nearby_message += " {0}".format(encounter["pokemon_id"])
                    # Otherwise it is a lingering nearby mon
                    else:
                        lingering_nearby = True
                        lingering_nearby_message += " {0}".format(encounter["pokemon_id"])

                # Refresh our experienced encounters
                # This will delete stale encounters
                cur_encounters = new_encounters

                # Notification of consolidated nearby mon
                if new_nearby:
                    print nearby_message
                    sendmessage(nearby_message)
                    cur_nearby.update(new_nearby)

                # Terminal message of lingering nearby mon
                if lingering_nearby:
                    print lingering_nearby_message

                printline()
                print ""
        # Handle other (likely 5XX) errors.
        except:
            print "Error reaching servers..."
            tries += 1
            pass

    human_delay = random.randint(1, 20)
    # Delay until next cycle
    # Add random few seconds to make us look less like a bot
    sleep(DELAY * 60 + human_delay)

