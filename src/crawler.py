import requests
import json
import time

def main():
    # Specifies API to return JSON
    headers = {"Accept": "application/json"}

    # JSON files to write to
    projects_json = open("projects.json", "a")

    # Initial setup
    nextProjectId = 2
    hasNext = True
    projects = []
    error_count = 0

    while hasNext:
        # Requesting projects from Global Giving API
        try:
            r = requests.get(
                "https://api.globalgiving.org/api/public/projectservice/all/projects/"
                + "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId="
                + str(nextProjectId),
                headers=headers,
            )

            projects = r.json()["projects"]
        
        except:
            error_count += 1
            if error_count >= 3:
                nextProjectId += 1
                error_count = 0
            continue

        # Grabbing next projects
        hasNext = projects["hasNext"]
        if hasNext:
            nextProjectId = projects["nextProjectId"]

        # Recording projects
        projects += [
            parseProjectInfo(project, label=True) for project in projects["project"]
        ]

        time.sleep(0.5)

    # Writing projects to JSON file
    json.dump(
        {"projects": projects},
        projects_json,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def getProjectKey(project, keys):
    """
    Helper method to find project properties
    Finds properties in given keys, if not, returns ''
    """
    try:
        result = project
        for key in keys:
            result = result[key]  # .get
        return result
    except:
        return ""


# Helper method to parse projects and filter relevant data
def parseProjectInfo(project, label):
    # Unlabeled data to return
    name = getProjectKey(project, ["organization", "name"])
    url = getProjectKey(project, ["organization", "url"])
    country = getProjectKey(project, ["country"])
    themes = getProjectKey(project, ["organization", "themes", "theme"])
    return {"name": name, "url": url, "themes": themes, "country": country}

if __name__ == "__main__":
    main()
