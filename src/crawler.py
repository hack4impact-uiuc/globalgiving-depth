import requests
import json
import time

# Parsing each project for relevant data
def project_info(project, label):
    if label:
        themes = ''
        try:
            themes = project['organization']['themes']['theme']
        except:
            pass
    name = ''
    url = ''
    country = ''


    # can it be cleaned up???
    try:
        name = project['organization']['name']
    except:
        pass
    try:
        url = project['organization']['url']
    except:
        pass
    try:
        country = project['country']
    except:
        pass
    if label:
        return {'name': name, 'url': url, 'themes': themes, 'country': country}
    return {'name': name, 'url': url, 'country': country}

# JSON instead of XML
headers = {'Accept': 'application/json'}

# JSON files to write to
labeled_results_json = open('labeled_results.json', 'w')
unlabeled_results_json = open('unlabeled_results.json', 'w')


# Starting project iteration
nextProjectId = 2
hasNext = True
labeled_results = []
unlabeled_results = []

while hasNext:
    # request and parsing each project in the request
    r = requests.get("https://api.globalgiving.org/api/public/projectservice/all/projects/" + 
                     "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId=" + str(nextProjectId), 
                     headers=headers)

    projects = r.json()['projects']
    hasNext = projects['hasNext']
    if hasNext:
        nextProjectId = projects['nextProjectId']
    labeled_results += [project_info(project, label=True) for project in projects['project']]
    unlabeled_results += [project_info(project, label=False) for project in projects['project']]

    time.sleep(30)

json.dump({'projects': unlabeled_results}, unlabeled_results_json, sort_keys= True, indent = 2, ensure_ascii = False)
json.dump({'projects': labeled_results}, labeled_results_json, sort_keys=True, indent = 2, ensure_ascii = False)
