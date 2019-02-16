import requests
import json
import time

# Helper method to find project properties
def getProjectKey(project, keys):
    # Finds properties in given keys, if not, returns ''
    try: 
        result = project
        for key in keys:
            result = result[key]
        return result
    except:
        return ''


# Helper method to parse projects and filter relevant data
def parseProjectInfo(project, label):
    # Unlabeled data to return
    name = getProjectKey(project, ['organization', 'name'])
    url = getProjectKey(project, ['organization', 'url'])
    country = getProjectKey(project, ['country'])

    # Labeled data to return if wanted
    if label:
        themes = getProjectKey(project, ['organization', 'themes', 'theme'])
        return {'name': name, 'url': url, 'themes': themes, 'country': country}

    return {'name': name, 'url': url, 'country': country}


# Specifies API to return JSON
headers = {'Accept': 'application/json'}

# JSON files to write to
labeled_results_json = open('labeled_results.json', 'a')
unlabeled_results_json = open('unlabeled_results.json', 'a')

# Initial setup
nextProjectId = 343
hasNext = True
labeled_results = []
unlabeled_results = []

try:
    while hasNext:
        # Requesting projects from Global Giving API
        r = requests.get("https://api.globalgiving.org/api/public/projectservice/all/projects/" + 
                        "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId=" + str(nextProjectId), 
                        headers=headers)
        
        projects = r.json()['projects']

        # Grabbing next projects
        hasNext = projects['hasNext']
        if hasNext:
            nextProjectId = projects['nextProjectId']

        # Recording projects
        labeled_results += [parseProjectInfo(project, label=True) for project in projects['project']]
        unlabeled_results += [parseProjectInfo(project, label=False) for project in projects['project']]

        time.sleep(30)

except Exception as e:
    print(e)
    print('nextProjectId = ' + str(nextProjectId))

# Writing projects to JSON file
json.dump({'projects': labeled_results}, labeled_results_json, sort_keys=True, indent = 2, ensure_ascii = False)
json.dump({'projects': unlabeled_results}, unlabeled_results_json, sort_keys= True, indent = 2, ensure_ascii = False)
