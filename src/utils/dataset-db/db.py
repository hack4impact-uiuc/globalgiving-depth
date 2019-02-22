import os
import json
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


def upload_many(organizations: list) -> bool:
    """
    This method provides a way to upload all organizations found through the
    GlobalGiving public API. It avoids uploading duplicate organizations by
    first checking if it already exists.
    Input:
        organizatons: this is list of org dictionaries
    Output:
        a boolean flag which indicates the success of the upload
    """
    # it would be really easy to try to upload one organization outside of a
    # list, but this use case is not anticipated to be the primary one
    if not isinstance(organizations, list):
        return False

    db_collection = get_collection()

    # Go through each organization and upsert it to the database. This means
    # that we look for an existing record that matches the candidate record. If
    # we find a match, we update. If not, we insert.
    for org in organizations:
        db_collection.update(org, org, {upsert: True})

    return True


def upload_from_file(filepath: str) -> bool:
    """
    Method to upload organizations from a given filepath.
    Input:
        filepath: a string which locates the json file containing orgs
    Output:
        a boolean flag which indicates success
    """
    pass


if __name__ == "__main__":
    assert upload_from_file("../../get-orgs/orgs.json")
