import boto3
import dotenv
import os
import json


db_client = None
tables_by_name = {}


def db_init():
    '''
    Method to initialize connection to dynamoDB.
    Input:
        None.
    Output:
        connection: a boto3.dynamodb.client instance representing
                           the connection you've created.
    '''
    assert dotenv.load_dotenv()
    AWS_KEY_ID = os.getenv("AWS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    client = boto3.client(
            'dynamodb',
            aws_access_key_id=AWS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_KEY,
            region='us-east-2')

    return client


def get_table(client, table_name):
    # deprecated!
    '''
    Method to retrieve a table object from a dynamoDB.
    Input:
        table_name: a string representing the name of the table you wish to
                    retrieve
        layer2_connection: an active connection to a dynamoDB instance
    Output:
        table: a boto.dynamodb.table.Table object specified by table_name
    '''
    assert client is not None
    table = tables_by_name.get(table_name)
    if table is None:
        table = client.get_table(table_name)
        assert table is not None
        tables_by_name[table_name] = table

    return table

def get_all_items(client, table_name):
    '''
    Method to retrieve all items from a table.
    Input:
        table_name: a string representing the name of the table you wish to get
        layer2_connection: an active connection to a dynamoDB instance
    Output:
        table: a boto.dynamodb.table.Table object specified by table_name
    '''
    items = []
    response = {"LastEvaluatedKey": "notNone"}
    while(response.get("LastEvaluatedKey")):
        response = client.scan(table_name)
    return items


def put_many(client, table_name, item_list):
    '''
    Method to put a list of JSON items in a table.
    Input:
        table: the name of the table you wish to add to
        item_list: a list of JSON structs containing the items' fields
    Output:
        boolean: success or fail
    '''
    item_count = 0
    for item in item_list:
        try:
            put_item(client, table_name, item)
        except(Exception):
            print("failed to upload item at lindex: " +
                  str(item_list.index(item)))
            continue
        item_count += 1
    print("Uploaded " + str(item_count) + " / " + str(len(item_list)) +
          " items.")
    return item_count


def put_item(client, table_name, item):
    '''
    Method to put an individual JSON item in a table.
    Input:
        client: a boto3.client object
        table_name: name of table you're adding to
        item: a JSON struct containing the item's fields
    Output:
        dict: containing attributes of new item
    '''
    new_item = client.put_item(
        TableName=table_name,
        Item=item
    )
    return new_item


if __name__ == "__main__":
    db_client = db_init()
