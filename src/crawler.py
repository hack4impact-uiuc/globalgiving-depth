import requests
import json
import time
import os
from dotenv import load_dotenv


def main():
    load_dotenv()

    global_giving_key = os.getenv("GLOBAL_GIVING_KEY")

    # Specifies API to return JSON
    headers = {"Accept": "application/json"}

    # JSON files to write to
    projects_json = open("projects.json", "w")

    # Initial setup
    next_project_id = 2
    has_next = True
    projects_list = []
    error_count = 0

    while has_next:
        # Requesting projects from Global Giving API
        try:
            r = requests.get(
                "https://api.globalgiving.org/api/public/projectservice/all/projects/"
                + "?api_key="
                + str(global_giving_key)
                + "&next_project_id="
                + str(next_project_id),
                headers=headers,
            )
            projects = r.json()["projects"]
            # json.dump(
            #     projects["project"],
            #     projects_json,
            #     sort_keys=True,
            #     indent=2,
            #     ensure_ascii=False,
            # )
        except:
            error_count += 1
            if error_count >= 3:
                next_project_id += 1
                error_count = 0
            continue

        # Grabbing next projects
        has_next = projects["hasNext"]
        if has_next:
            next_project_id = projects["nextProjectId"]

        # Recording projects
        projects_list += [
            parse_project_info(project) for project in projects["project"]
        ]
        break
        time.sleep(0.5)

    # Writing projects to JSON file
    json.dump(
        {"projects": projects_list},
        projects_json,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def get_project_key(project, keys):
    """
    Helper method to find project properties
    Finds properties in given keys, if not, returns ''
    """
    result = project
    for key in keys:
        result = result.get(key)
    if result is not None:
        return result
    return ""


# Helper method to parse projects and filter relevant data
def parse_project_info(project):
    # data to return
    name = get_project_key(project, ["organization", "name"])
    url = get_project_key(project, ["organization", "url"])
    main_theme = get_project_key(project, ["themeName"])
    sub_themes = get_project_key(project, ["organization", "themes", "theme"])
    country = get_project_key(project, ["country"])

    return {
        "name": name,
        "url": url,
        "mainTheme": main_theme,
        "subThemes": sub_themes,
        "country": country,
    }


if __name__ == "__main__":
    main()
