from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

def connect_to_db():
    # Load the environment variables
    load_dotenv()

    # Replace the placeholder with your Atlas connection string
    uri = os.getenv("MONGO_URI")

    # Set the Stable API version when creating a new client
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client

    except Exception as e:
        print(e)
