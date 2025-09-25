from datetime import datetime
from re import search

from db.database import get_db
from db.dbSchema import PatientData

from surrealdb import RecordID

async def CreateWAMessageEntryService(
        chat_name, 
        name, 
        iso_time, 
        message_text,
        db=None
    ):
    """Create an entry in the database"""
    try:    
        # If no db is provided, get one
        if db is None:
            db = await get_db()
            
        # print("CreateEntryService: \n")    
        # print(f"----- \n Chat Name: {chat_name} \n Sender: {name} \n Time: {iso_time} \n Nachricht: {message_text} \n -------")

        # Replace spaces with underscores in chat_name and name
        chat_name = chat_name.replace(" ", "_")
        name = name.replace(" ", "_")

        # Create a record with a specific ID
        result = await db.create(RecordID('Message', f'{chat_name}:{name}:{iso_time}'), {
            "chat_name": chat_name,
            "name": name,
            "time": iso_time,
            "message": message_text,
            "entry_creation": datetime.now().isoformat()
        })
        
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