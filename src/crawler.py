import requests
import json

headers = {'Accept': 'application/json'}
r = requests.get("https://api.globalgiving.org/api/public/projectservice/projects/collection/summary/ids?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&projectIds=123,1883", headers=headers)

projects = r.json()['projects']

for project in projects['project']:
    print(project)
    print()