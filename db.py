from pymongo import MongoClient

def get_db_connection():
    # Replace the following with your MongoDB connection details
    username = 'gitfeed'
    password = 'gitfeedio123'
    host = 'localhost'
    port = 27017  # Default MongoDB port
    database = 'gitfeed'

    # Create the MongoDB connection string
    connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"

    # Connect to MongoDB
    client = MongoClient(connection_string)

    # Access the database
    db = client[database]
    return db

if __name__ == "__main__":
    db = get_db_connection()
    print("Connected to MongoDB!")