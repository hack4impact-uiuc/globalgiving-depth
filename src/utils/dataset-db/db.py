import os
import json
import hashlib
import dotenv
import pymongo


def get_collection() -> pymongo.collection.Collection:
    """
    This is a small method to retreive the uri from the environment and get the
    collection from the database, so we don't have to do it in every single
    other function in this file.
    Output: a database collection object
    """
    # load the URI from the environment
    assert dotenv.load_dotenv()
    uri = os.getenv("MONGO_DB_URI")

    # get the collection from the database
    client = pymongo.MongoClient(uri)
    db_collection = client.ggdb.organizations
    return db_collection


def get_dataset(simple=False) -> list:
    """
    This method retreives the dataset of NGO records from the mongodb instance.
    Input:
        simple: we may also retreive simplified records which are only
        `{"name": name, "url":url}`.
    Output:
        dataset: a list containing dictionaries of NGO records
    """
    db_collection = get_collection()  # get the collection
    dataset = [org for org in db_collection.find()]  # store all orgs in list

    # pick out only the name and url if we've queried with `simple=True`
    if simple:
        dataset = list(
            map(lambda org: {"name": org["name"], "url": org["url"]}, dataset)
        )

    return dataset


def upload_many(organizations: list):
    """
    This method provides a way to upload all organizations found through the
    GlobalGiving public API. It avoids uploading duplicate organizations by
    first checking if it already exists.
    Input:
        organizatons: this is list of org dictionaries
    """
    # it would be really easy to try to upload one organization outside of a
    # list, but this use case is not anticipated to be the primary one
    if not isinstance(organizations, list):
        return

    # Create an id for each document. Hopefully these are unique enough to
    # avoid collisions where necessary, but not unique enough to get duplicate
    # records.
    for org in organizations:
        org.update(
            _id=hashlib.md5((org["name"] + org["url"]).encode("utf-8")).hexdigest()
        )

    db_collection = get_collection()

    # Go through each organization and upsert it to the database. Use the name
    # concatenated with the url as the id. If there is an id collision, skip
    # the organization. `ordered=False` so all inserts will be attempted.
    try:
        db_collection.insert_many(organizations, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        print(json.dumps(dict(bwe.details), indent=2))


def upload_from_file(filepath: str):
    """
    Method to upload organizations from a given filepath.
    Input:
        filepath: a string which locates the json file containing orgs
    Output:
        a boolean flag which indicates success
    """
    # open the file and read in the list
    with open(filepath, "r") as json_file:
        orgs = json.load(json_file)
    # send to upload
    upload_many(orgs)


if __name__ == "__main__":
    upload_from_file("../../get-orgs/orgs.json")
