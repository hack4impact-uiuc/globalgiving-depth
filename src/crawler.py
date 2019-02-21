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
    with open("orgs.json", "w") as orgs_json:

        r = requests.get("https://api.globalgiving.org/api/public/orgservice/all/organizations" +
                        "?api_key=" + 
                        global_giving_key,
                        headers=headers)

        # Initial setup
        next_org_id = r
        has_next = True
        orgs_list = []
        error_count = 0

        # 30000 is so the loop doesn't run forever if we get a 400 because there are around 25000 orgs
        while has_next and next_org_id < 30000:
            # Requesting orgs from Global Giving API
            r = requests.get("https://api.globalgiving.org/api/public/orgservice/all/organizations" +
                            "?api_key=" + 
                            global_giving_key +
                            "&nextOrgId=" +
                            str(next_org_id),
                            headers=headers)

            orgs = r.json().get("orgs")
            print(next_org_id)

            if r.status_code != 200:
                print(r.status_code)
                error_count += 1
                if error_count >= 3:
                    next_org_id += 1
                    error_count = 0
                continue

            if orgs is None:
                print("No orgs" + str(next_org_id))
                break

            # Grabbing next orgs
            has_next = orgs["hasNext"]
            if has_next:
                next_org_id = orgs.get("nextOrgId")

            # Recording orgs
            orgs_list += [
                parse_org_info(org) for org in orgs["organization"]
            ]
            time.sleep(0.5)

        # Removing duplicate organizations
        orgs_list = remove_duplicate_organizations(orgs_list)

        # Writing orgs to JSON file
        json.dump(
            orgs_list,
            orgs_json,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )


def get_org_key(org, keys):
    """ Helper method to find org properties
    Finds properties in given keys, if not, returns ''

    Args: 
        org: orgs json returned by Global Giving's API
        keys: keys to iterate through org to find desired value

    Return:
        Object found in org key(s)
    """
    result = org
    for key in keys:
        result = result.get(key)
    if result is not None:
        return result
    return ""


def parse_org_info(org):
    """ Helper method to parse orgs and filter relevant data 

    Args:
        org: orgs json returned by Global Giving's API

    Return: 
        Dictionary of filtered parameters from org json
    """
    name = get_org_key(org, ["organization", "name"])
    url = get_org_key(org, ["organization", "url"])
    sub_themes = get_org_key(org, ["organization", "themes", "theme"])
    country = get_org_key(org, ["organization", "country"])

    return {
        "name": name,
        "url": url,
        "subThemes": sub_themes,
        "country": country,
    }


def remove_duplicate_organizations(orgs):
    """ super rough method to remove duplicates pls no judge """
    # Initializing set and list and size trackers
    organizations = {"empty"}
    organizations.remove("empty")
    cleaned_orgs = []
    initSize = 0
    afterSize = 0

    for org in orgs:
        initSize = len(organizations)
        organizations.add(org["name"])
        afterSize = len(organizations)

        if initSize < afterSize:
            cleaned_orgs.append(org)

    return cleaned_orgs


if __name__ == "__main__":
    main()
