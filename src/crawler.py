import requests
import json
import time
import os
import sys
from dotenv import load_dotenv


def main():
    """ 
    Retrieves and parses information from Global Giving's API
    and writes it to a json file 
    """

    # Loads global giving api key
    load_dotenv()
    global_giving_key = os.getenv("GLOBAL_GIVING_KEY")

    # Specifying API to return JSON
    headers = {"Accept": "application/json"}

    # Extracting organizations from API
    with open("orgs.json", "w") as orgs_json:
        r = requests.get(
            "https://api.globalgiving.org/api/public/orgservice/all/organizations"
            + "?api_key="
            + global_giving_key,
            headers=headers,
        )
        orgs = r.json().get("organizations")

        if orgs is None:
            print("No orgs")
            sys.exit(1)

        # Initial setup
        next_org_id = orgs.get("nextOrgId")
        has_next = orgs.get("hasNext")
        orgs_list = [parse_org_info(org) for org in orgs["organization"]]
        error_count = 0
        last_non_error = 0

        while has_next:
            # Requesting orgs from Global Giving API
            r = requests.get(
                "https://api.globalgiving.org/api/public/orgservice/all/organizations"
                + "?api_key="
                + global_giving_key
                + "&nextOrgId="
                + str(next_org_id),
                headers=headers,
            )
            orgs = r.json().get("organizations")

            # Checking for status errors
            if r.status_code != 200:
                if next_org_id - 20 > last_non_error:
                    break
                print(r.status_code)
                error_count += 1
                if error_count >= 3:
                    next_org_id += 1
                    error_count = 0
                continue

            if orgs is None:
                print("No orgs")
                break

            last_non_error = orgs["organization"][-1].get("id")

            # Grabbing next orgs
            has_next = orgs.get("hasNext")
            if has_next:
                next_org_id = orgs.get("nextOrgId")

            # Recording orgs
            orgs_list += [parse_org_info(org) for org in orgs["organization"]]
            time.sleep(0.5)

        # Writing orgs to JSON file
        json.dump(orgs_list, orgs_json, sort_keys=True, indent=2, ensure_ascii=False)


def get_org_key(org, keys):
    """ 
    Helper method to find org properties
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
    """ 
    Helper method to parse orgs and filter relevant data 

    Args:
        org: orgs json returned by Global Giving's API

    Return: 
        Dictionary of filtered parameters from org json
    """
    name = org.get("name")
    url = org.get("url")
    themes = org.get("themes").get("theme")
    country = org.get("country")

    return {"name": name, "url": url, "themes": themes, "country": country}


if __name__ == "__main__":
    main()
