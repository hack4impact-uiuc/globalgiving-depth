import requests
import json
import time

# Filters essential information from project
def project_info(project):
    name = ''
    url = ''
    themes = ''
    country = ''
    try:
        name = project['organization']['name']
    except:
        pass
    try:
        url = project['organization']['url']
    except:
        pass
    try:
        themes = project['organization']['themes']["theme"]
    except:
        pass
    try:
        country = project['country']
    except:
        pass
    return {'name': name, 'URL': url, 'themes': themes, 'country': country}

# Initial setup
headers = {'Accept': 'application/json'} # returns data from api in json format
nextProjectId = 2
hasNext = True
file = open("projects.json", "w")
results = []

# Grabbing data from api and writing it to a file
for i in range(2):
    # Getting projects from global giving api
    r = requests.get("https://api.globalgiving.org/api/public/projectservice/all/projects/" + 
                    "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId=" + str(nextProjectId), 
                    headers=headers)
    projects = r.json()['projects']

    # Grabbing next projects
    hasNext = projects['hasNext']
    if hasNext:
        nextProjectId = projects['nextProjectId']

    # Storing filtered projects into list
    results += [project_info(project) for project in projects['project']]
        
    # TODO: time.sleep(60)
    time.sleep(5)

# Writing json to outfile
json.dump({'projects' : results}, file, sort_keys = True, indent = 4, ensure_ascii = False)

# Method to open json and access projects for future use
'''with open("projects.json", "r") as json_file:
    projects = json.load(json_file)
    print(projects[15]['id'])'''