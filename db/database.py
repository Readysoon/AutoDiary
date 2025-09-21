from surrealdb import Surreal, AsyncSurreal
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
DATABASE_USER = os.getenv("SURREALDB_USER")
DATABASE_PASS = os.getenv("SURREALDB_PASS")
DATABASE_NAMESPACE = os.getenv("SURREALDB_NAMESPACE")
DATABASE_NAME = os.getenv("SURREALDB_DATABASE")

async def get_db():
    """Database dependency that provides a connected and authenticated SurrealDB instance"""
    db = None
    try:
        print("This is the updated db connection 3")
        print(DATABASE_URL, DATABASE_USER, DATABASE_PASS, DATABASE_NAMESPACE, DATABASE_NAME)
        
        # Initialize the database connection
        db = AsyncSurreal(DATABASE_URL)
        
        # Connect to the database
        await db.connect()
        
        # Select namespace and database
        await db.use(DATABASE_NAMESPACE, DATABASE_NAME)

        # Sign in to the database
        await db.signin({
            "username": DATABASE_USER,
            "password": DATABASE_PASS
        })

        return db
        
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Database connection failed: {str(e)}")










