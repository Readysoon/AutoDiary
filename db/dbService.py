from datetime import datetime
from re import search

from db.database import get_db
from db.dbSchema import PatientData

from surrealdb import RecordID

async def CreateEntryService(
        entry, 
        db=None
    ):
    """Create an entry in the database"""
    try:    
        # If no db is provided, get one
        if db is None:
            db = await get_db()
            
        print("CreateEntryService: ", entry)    
        
        # Handle both dictionary and Pydantic object
        if isinstance(entry, dict):
            entry_data = entry.copy()
        else:
            # If it's a Pydantic object, convert to dict
            entry_data = entry.model_dump() if hasattr(entry, 'model_dump') else entry.dict()
        
        # Add today's date and time
        
        entry_data["created_datetime"] = datetime.now().isoformat()

        result = await db.create("PatientenTermin", entry_data)
        
        return {
            "status": "success", 
            "result": result
        }

    except Exception as e:
        raise Exception(f"Database operation failed: {str(e)}")


async def GetEntryService(db=None, search_string=str):
    """Get all entries from the database"""
    try:     
        # If no db is provided, get one
        if db is None:
            db = await get_db()
            
        print("GetEntryService: Fetching the entry")    

        result = await db.select(RecordID('example_table', search_string))

        return result['Fenster']

    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")