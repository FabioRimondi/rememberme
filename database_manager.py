import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os


# Server MongoDB
client = MongoClient(host=os.environ['rememberme_mongoip'],
            port=27017,
            username= os.environ['rememberme_mongouser'],
            password= os.environ['rememberme_mongopass'],
            connect=True,
            authSource= os.environ['rememberme_mongoauthsource'])

# Database MongoDB
db = client[os.environ['rememberme_mongodb']]       
# Collection
remembers = db.remembers

