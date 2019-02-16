import requests
import json
import time

def main():
    # Specifies API to return JSON
    headers = {"Accept": "application/json"}

    # JSON files to write to
    labeled_results_json = open("labeled_results.json", "a")

    # Initial setup
    next_project_id = 2
    has_next = True
    labeled_results = []

    try:
        while has_next:
            # Requesting projects from Global Giving API
            r = requests.get(
                "https://api.globalgiving.org/api/public/projectservice/all/projects/"
                + "?api_key=72ef6e29-cb2b-4613-9cc6-69a88a8d3f3b&nextProjectId="
                + str(next_project_id),
                headers=headers,
            )

            projects = r.json()["projects"]

            # Grabbing next projects
            has_next = projects["hasNext"]
            if has_next:
                next_project_id = projects["nextProjectId"]

            # Recording projects
            labeled_results += [
                parse_project_info(project) for project in projects["project"]
            ]

            time.sleep(0.5)

    except Exception as e:
        print(e)
        print("nextProjectId = " + str(next_project_id))

    # Writing projects to JSON file
    json.dump(
        {"projects": labeled_results},
        labeled_results_json,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def get_project_key(project, keys):
    """
    Helper method to find project properties
    Finds properties in given keys, if not, returns ''
    """
    try:
        result = project
        for key in keys:
            result = results.get(key)
        return result
    except:
        return ""


# Helper method to parse projects and filter relevant data
def parse_project_info(project):
    # Unlabeled data to return
    name = get_project_key(project, ["organization", "name"])
    url = get_project_key(project, ["organization", "url"])
    main_theme = get_project_key(project, ["themeName"])
    sub_themes = get_project_key(project, ["organization", "themes", "theme"])
    country = get_project_key(project, ["country"])
    
    return {"name": name, "url": url, "mainTheme": main_theme, "subThemes": sub_themes, "country": country}

if __name__ == "__main__":
    main()