import db
import json
import bson

def load_bson_data(file_path, limit=10):
    data = []
    with open(file_path, 'rb') as file:
        for i, item in enumerate(bson.decode_file_iter(file)):
            if i >= limit:
                break
            data.append(item)
    return data

def print_events():
    mongodb = db.get_db_connection()
    events_collections = mongodb['events']

    # Find all documents where type is "IssuesEvent"
    issues_events = events_collections.find({"type": "PushEvent"}).limit(10)

    # Pretty print the resulting documents
    for event in issues_events:
        print(json.dumps(event, indent=4, default=str))


if __name__ == "__main__":
    file_path = './dump/gitfeed/events.bson'
    data = load_bson_data(file_path, 10000)
    print(json.dumps(data, indent=4, default=str))