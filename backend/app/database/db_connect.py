from pymongo import MongoClient
from pymongo.server_api import ServerApi
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
# MongoDB connection (Replace with your MongoDB URI)

def mongo():

    client = MongoClient(os.getenv("DATABASE"), server_api=ServerApi(
    version="1", strict=True, deprecation_errors=True))
    return client

def connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the service account JSON file
    json_path = os.path.join(current_dir, "Service_Account.json")

    # Check if the Firebase app has already been initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_path)  # Path to the service account key JSON file
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'hack-e5746.appspot.com',
            'databaseURL':"https://hack-e5746-default-rtdb.firebaseio.com"
        })

    # Get Firestore client
    db = firestore.client()
    # Retrieve Firebase Storage bucket instance
    return db