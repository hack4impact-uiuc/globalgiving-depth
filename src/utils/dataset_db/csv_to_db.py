from db import upload_many
import csv
import sys


def csv_upload(csv_path):
    """
    Given a CSV file, this method uploads it to the organizations-unlabelled
    collection.
    """
    orgs = []
    with open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
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

        print("Records parsed:", line_count)

    upload_many(orgs, db_collection=get_collection("organizations_unlabelled"))


if __name__ == "__main__":
    csv_upload(sys.argv[1])
