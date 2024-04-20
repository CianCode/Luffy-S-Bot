# Description: This file contains the code to connect to the MongoDB database.

# * Import the necessary libraries
import os
import motor.motor_asyncio
from dotenv import load_dotenv

# * Load the environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

# * Create the MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client['LuffyDB']

# * Create the MongoDB collections
reputation_roles = db['reputation_roles'] # ? Collection to store the reputation roles
reputation_members = db['reputation_members'] # ? Collection to store the reputation of the users
reputation_channels = db['reputation_channels'] # ? Collection to store the reputation channels