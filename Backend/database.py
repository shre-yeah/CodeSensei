import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Load environment variables from the .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print("MONGODB_URL:", MONGODB_URL)
print("DATABASE_NAME:", DATABASE_NAME)

class Database:
    client: AsyncIOMotorClient = None
    
database = Database()

async def get_database():
    """Dependency to get database instance"""
    return database.client[DATABASE_NAME]

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    print("Connecting to MongoDB...")
    database.client = AsyncIOMotorClient(MONGODB_URL)
    print("Connected to MongoDB!")
    
async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    print("Closing MongoDB connection...")
    database.client.close()
    print("MongoDB connection closed!")