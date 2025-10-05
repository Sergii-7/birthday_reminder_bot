"""
MongoDB connection setup using Motor (asynchronous MongoDB driver).
Do not use in this project, because PostgreSQL is main DataBase.
"""

from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)

db = client.BirthdayBot
