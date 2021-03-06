from __future__ import print_function
from datetime import date, timedelta
import json
import os
import requests
import sys

forensics_file = os.path.join(os.environ["SPLUNK_HOME"], "etc", "apps", "twistlock", "bin", "meta", "forensics_events.txt")
config_file = os.path.join(os.environ["SPLUNK_HOME"], "etc", "apps", "twistlock", "bin", "meta", "config.json")
config = json.load(open(config_file))

console_fqdn = config["setup"]["console_fqdn"]
endpoint = "/api/v1/profiles/"

username = config["credentials"]["username"]
password = config["credentials"]["password"]

if (os.path.isfile(forensics_file)):
    field_extracts = json.load(open(forensics_file))

    for field in field_extracts:
        url = console_fqdn + endpoint + field["type"] + "/" + field["profileID"] + "/forensic?hostname=" + field["hostname"] + "&limit=500"
        response = requests.get(url, auth=(username, password))
        try:
            json_response = response.json()
        except ValueError:
            print("ValueError with URL:", url, file=sys.stderr)
            exit(1)

        if json_response is not None:
            # Add hostname field for matching host incident to forensic data
            if (field["type"] == "host"):
                for element in json_response:
                    element["hostname"] = field["hostname"]
                    print(json.dumps(element))
            else:
                for element in json_response:
                    print(json.dumps(element))

    os.remove(forensics_file)
else:
    print("No forensics: forensics file not created by poll-incidents.py", file=sys.stderr)
