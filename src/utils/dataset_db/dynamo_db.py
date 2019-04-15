import boto3
import dotenv
import os


Db_client = None
Tables_by_name = {}


def get_dataset(table_name):
    """
    This function returns an entire table from a table name. This is the
    function that should be used in external modules/algorithms.
    Input:
        table_name: string, the name of the table you're querying
    Output:
        data: list of JSON objects representing the table.
    """
    client = db_init()
    table = get_table(client, table_name)
    data = get_all_items(table)
    return data


def put_dataset(table_name, item_list):
    """
    This function uploads a list of JSON objects to a table specified by
    table_name. This is the function that should be used in external modules/
    algorithms.
    Input:
        table_name: string, the name of the table you're uploading to
        item_list: list of dicts, items you're uploading.
    Output:
        item_count: number of items successfully uploaded.
    """
    client = db_init()
    table = get_table(client, table_name)
    item_count = put_many(table, item_list)
    return item_count


def db_init():
    """
    Method to initialize connection to dynamoDB.
    Input:
        None.
    Output:
        connection: a boto3.resource instance representing
                           the connection you've created.
    """
    assert dotenv.load_dotenv()
    AWS_KEY_ID = os.getenv("AWS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    client = boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="us-east-2",
    )

    return client


def get_table(client, table_name):
    """
    Method to retrieve a table object from a dynamoDB.
    Input:
        table_name: a string representing the name of the table you wish to
                    retrieve
        layer2_connection: an active connection to a dynamoDB instance
    Output:
        table: a boto.dynamodb.table.Table object specified by table_name
    """
    assert client is not None
    table = Tables_by_name.get(table_name)
    if table is None:
        table = client.Table(table_name)
        assert table is not None
        Tables_by_name[table_name] = table

    return table


def get_all_items(table):
    """
    Method to retrieve all items from a table.
    Input:
        table: a table object, the table you wish to get
    Output:
        data: a list of all JSON objects from the table
    """
    response = table.scan()
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])
    return data


def put_many(table, item_list):
    """
    Method to put a list of JSON items in a table.
    Input:
        table: the table object you wish to add to
        item_list: a list of JSON structs containing the items' fields
    Output:
        item_count: number of items uploaded successfully
    """
    item_count = 0
    for item in item_list:
        try:
            put_item(table, item)
        except Exception as e:
            print("failed to upload item at lindex: " + str(item_list.index(item)))
            print(e)
            continue
            # remove above continue to add records with missing fields anyways
            print("Trying again without empty strings")
            for k, v in item.items():
                if v == "":
                    item[k] = "none"
            try:
                put_item(table, item)
                print("Success!")
            except Exception as e2:
                print("failed again.")
                print(e2)
                continue
        item_count += 1
    print("Uploaded " + str(item_count) + " / " + str(len(item_list)) + " items.")
    return item_count


def put_item(table, item):
    """
    Method to put an individual JSON item in a table.
    Input:
        table_: table object you're adding to
        item: a JSON struct containing the item's fields
    Output:
        new_item: dict containing metadata from request
    """
    new_item = table.put_item(Item=item)
    return new_item


if __name__ == "__main__":
    Db_client = db_init()