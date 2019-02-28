from db import upload_many
import json
import csv
import os
import sys
import pymongo
import dotenv

def csv_upload(csv_path):
    '''
    Given a CSV file, this method uploads it to the organizations-unlabelled
    collection.
    '''
    orgs = []
    with open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                org = {}
                org["gg_id"] = row[0]
                org["name"] = row[1]
                org["url"] = row[2]
                orgs.append(org)
                line_count += 1

        print("Records parsed:",line_count)

    upload_many(orgs, db_collection=get_unlabelled_collection())


def get_unlabelled_collection() -> pymongo.collection.Collection:
    """
    Stole this method from db.py to get the unlabelled collection instead.
    """
    # load the URI from the environment
    assert dotenv.load_dotenv()
    uri = os.getenv("MONGO_DB_URI")

    # get the collection from the database
    client = pymongo.MongoClient(uri)
    db_collection = client.ggdb.organizations_unlabelled
    return db_collection

if __name__ == "__main__":
    csv_upload(sys.argv[1])
