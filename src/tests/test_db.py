import sys
import json
import mongomock

sys.path.append("..")

from src.utils.dataset_db import db  # custom module for database API


with open("tests/test_orgs.json", "r") as json_file:
    ORGS = json.load(json_file)


def test_upload_many():
    """
    test upload many
    """
    collection = mongomock.MongoClient().db.collection
    assert collection.count_documents({}) == 0  # empty
    db.upload_many(ORGS, collection)
    assert collection.count_documents({}) == 60  # insert all docs
    db.upload_many(ORGS, collection)
    assert collection.count_documents({}) == 60  # no duplicate insertions


def test_get_dataset():
    """
    test getting the entire dataset
    """
    dataset = db.get_dataset("organizations")
    assert dataset is not None            # did we even get anything?
    assert dataset[0]["name"]             # name shouldn't be blank in this collection
    assert dataset[0]["url"] is not None  # url might be blank, so test if None

    dataset = db.get_dataset("organizations_text")
    assert dataset is not None  # did we even get anything?
    assert dataset[0]["name"]   # name shouldn't be blank in this collection
    assert dataset[0]["url"]    # we should have urls in this collection

    dataset = db.get_dataset("organizations_text")
    assert dataset is not None  # did we even get anything?
    assert dataset[0]["name"]   # name shouldn't be blank in this collection
    assert dataset[0]["url"]    # we should have urls in this collection
    assert len(dataset) == 4995 # we know how many orgs are in this one
