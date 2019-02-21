import requests
import json
import time
import os
import sys
from dotenv import load_dotenv


def main():
    """ Retrieves and parses information from Global Giving's API
        and writes it to a json file """

    # loads global giving api key
    load_dotenv()
    global_giving_key = os.getenv("GLOBAL_GIVING_KEY")

    # Specifying API to return JSON
    headers = {"Accept": "application/json"}

    # JSON files to write to
    projects_json = open("projects.json", "w")

    r = requests.get("https://api.globalgiving.org/api/public/orgservice/all/organizations" +
                    "?api_key=" + 
                    global_giving_key,
                    headers=headers)

    # Initial setup
    next_org_id = 2
    has_next = True
    projects_list = []
    error_count = 0

    # 30000 is so the loop doesn't run forever if we get a 400 because there are around 25000 projects
    while has_next and next_org_id < 30000:
        # Requesting projects from Global Giving API
    r = requests.get("https://api.globalgiving.org/api/public/orgservice/all/organizations" +
                    "?api_key=" + 
                    global_giving_key +
                    "&nextOrgId=" +
                    str(next_org_id),
                    headers=headers)

        projects = r.json().get("projects")
        print(next_org_id)

        if r.status_code != 200:
            print(r.status_code)
            error_count += 1
            if error_count >= 3:
                next_org_id += 1
                error_count = 0
            continue

        if projects is None:
            print("No projects" + str(next_org_id))
            break

        # Grabbing next projects
        has_next = projects["hasNext"]
        if has_next:
            next_org_id = projects["nextProjectId"]

        # Recording projects
        projects_list += [
            parse_project_info(project) for project in projects["project"]
        ]
        time.sleep(0.5)

    # Removing duplicate organizations
    projects_list = remove_duplicate_organizations(projects_list)

    # Writing projects to JSON file
    json.dump(
        projects_list,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def get_project_key(project, keys):
    """ Helper method to find project properties
    Finds properties in given keys, if not, returns ''

    Args: 
        project: projects json returned by Global Giving's API
        keys: keys to iterate through project to find desired value

    Return:
        Object found in project key(s)
    """
    result = project
    for key in keys:
        result = result.get(key)
    if result is not None:
        return result
    return ""


def parse_project_info(project):
    """ Helper method to parse projects and filter relevant data 

    Args:
        project: projects json returned by Global Giving's API

    Return: 
        Dictionary of filtered parameters from project json
    """
    name = get_project_key(project, ["organization", "name"])
    url = get_project_key(project, ["organization", "url"])
    sub_themes = get_project_key(project, ["organization", "themes", "theme"])
    country = get_project_key(project, ["organization", "country"])

    return {
        "name": name,
        "url": url,
        "subThemes": sub_themes,
        "country": country,
    }


def remove_duplicate_organizations(projects):
    """ super rough method to remove duplicates pls no judge """
    # Initializing set and list and size trackers
    organizations = {"empty"}
    organizations.remove("empty")
    cleaned_projects = []
    initSize = 0
    afterSize = 0

    for project in projects:
        initSize = len(organizations)
        organizations.add(project["name"])
        afterSize = len(organizations)

        if initSize < afterSize:
            cleaned_projects.append(project)

    return cleaned_projects


if __name__ == "__main__":
    main()
