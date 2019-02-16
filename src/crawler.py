import requests
import json
import time

# Initial setup
headers = {'Accept': 'application/json'} # returns data from api in json format
nextProjectId = 2
hasNext = True
file = open("projects.json", "w")
results = []

# Grabbing data from api and writing it to a file
for i in range(2):
    r = requests.get("https://api.globalgiving.org/api/public/projectservice/all/projects/" + 
                    "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId=" + str(nextProjectId), 
                    headers=headers)

    projects = r.json()['projects']
    hasNext = projects['hasNext']
    if hasNext:
        nextProjectId = projects['nextProjectId']

    results += projects['project']
        
    # TODO: time.sleep(60)
    time.sleep(5)

json.dump(results, file, sort_keys = True, indent = 4, ensure_ascii = False)

# method to open json and access projects
'''with open("projects.json", "r") as json_file:
    projects = json.load(json_file)
    print(projects[15]['id'])'''