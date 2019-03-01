import sys
import json
import mongomock

sys.path.append("..")

from src.utils.dataset_db import db


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
    collection = mongomock.MongoClient().db.collection
    assert collection.count_documents({}) == 0  # empty
    db.upload_many(ORGS, collection)
    assert collection.count_documents({}) == 60  # insert all docs
    dataset = db.get_dataset(collection)
    assert dataset is not None
    assert len(dataset) == 60
