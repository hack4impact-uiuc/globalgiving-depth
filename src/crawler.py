import requests
import json
import time

headers = {'Accept': 'application/json'}

nextProjectId = 2
hasNext = True
while hasNext:
    r = requests.get("https://api.globalgiving.org/api/public/projectservice/all/projects/" + 
                     "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId=" + str(nextProjectId), 
                     headers=headers)

    projects = r.json()['projects']
    hasNext = projects['hasNext']
    if hasNext:
        nextProjectId = projects['nextProjectId']

    # print(json.dumps(projects, indent=4))
    for project in projects['project']:
        print(project['id'])
        
    # TODO: time.sleep(60)
    time.sleep(5)