from datetime import datetime, timedelta
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

        dt = datetime.fromisoformat(iso_time)
        date_str = dt.date().isoformat()  # e.g., "2025-09-25"
        time_str = dt.time().isoformat()  # e.g., "16:02:00+02:00"

        search_result = await GetEntryService(chat_name, name, iso_time)

        print(f"dbService.py: CreateWAMessageEntryService: Search result of GetEntryService: \n {search_result}")

        if search_result:
            print("Message already in DB!")

        else: 
            # Create a record with a specific ID
            result = await db.create(RecordID('Message', f'{chat_name}:{name}:{iso_time}'), {
                "chat_name": chat_name,
                "name": name,
                "date": f"{date_str}",
                "time": f"{time_str}",
                "message": message_text,
                "entry_creation": f"d'{datetime.now().isoformat()}'"
            })
            
            return {
                "status": "success", 
                "result": result
            }
        

    except Exception as e:
        raise Exception(f"Database operation failed: {str(e)}")


async def GetEntryService(
        chat_name, 
        name, 
        iso_time, 
        db=None
    ):
    """Get an Message entry by ID from the database"""
    try:     
        # If no db is provided, get one
        if db is None:
            db = await get_db()
            
        print(f"GetEntryService: Fetching the entry '{chat_name}:{name}:{iso_time}'")    

        result = await db.select(RecordID('Message', f'{chat_name}:{name}:{iso_time}'))

        return result

    except Exception as e:
        raise Exception(f"Database query failed ({chat_name}:{name}:{iso_time}): {str(e)}")



async def GetAllTodaysEntriesService(
        day,
        db=None
    ):
    """Get all Message entries from the database for today"""
    if db is None:
        db = await get_db()

    print(f"GetAllTodaysEntriesService: Fetching all today's entries for '{day}'")

    result = await db.query(
        f"SELECT * FROM Message WHERE date = '{day}'"
    )

    return result

    

