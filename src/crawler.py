import requests
import json
import time

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
        themes = project['themes']
    except:
        pass
    try:
        country = project['country']
    except:
        pass
    return {'project': {'Name': name, 'URL': url, 'Themes': themes, 'Country': country}}



headers = {'Accept': 'application/json'}

test_json = open('test.json', 'w')

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
        json.dump(project_info(project), test_json, sort_keys= True, indent = 2, ensure_ascii= False)
        # json.dump(project, test_json, sort_keys= True, indent = 2, ensure_ascii= False)


    # TODO: time.sleep(60)
    time.sleep(5)