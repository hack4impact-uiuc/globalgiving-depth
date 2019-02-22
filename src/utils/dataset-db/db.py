import os
import dotenv
import pymongo


def get_dataset(simple=False):
    """
    This method retreives the dataset of NGO records from the mongodb instance.
    Input:
        simple: we may also retreive simplified records which are only
        `{"name": name, "url":url}`.
    Output:
        dataset: a list containing dictionaries of NGO records
    """
    # load the URI from the environment
    assert dotenv.load_dotenv()
    uri = os.getenv("MONGO_DB_URI")

    # get the collection from the database
    client = pymongo.MongoClient(uri)
    db_collection = client.ggdb.organizations
    dataset = [org for org in db_collection.find()]

    # pick out only the name and url if we've queried with `simple=True`
    if simple:
        dataset = list(
            map(lambda org: {"name": org["name"], "url": org["url"]}, dataset)
        )

    return dataset

    def upload():
        """
        stub
        """
