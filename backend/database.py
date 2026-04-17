"""
MongoDB Database Connection Module
Uses Motor (async driver) for high-performance database operations.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "resume_bot"

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """Initialize MongoDB connection."""
        if cls.client is None:
            if not MONGODB_URI:
                print("[ERROR] MONGODB_URI not found in environment")
                return
            
            cls.client = AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            try:
                # The ping command is cheap and does not require auth
                await cls.client.admin.command('ping')
                cls.db = cls.client[DB_NAME]
                server_info = await cls.client.server_info()
                version = server_info.get('version', 'unknown')
                print(f"[OK] Connected to MongoDB: {DB_NAME} (v{version})")
            except Exception as e:
                print(f"[ERROR] Could not connect to MongoDB: {str(e)}")
                cls.client = None

    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("[INFO] Disconnected from MongoDB")

async def get_db():
    if Database.db is None:
        await Database.connect()
    return Database.db
