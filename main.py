from fastapi import FastAPI, Depends

from surrealdb import Surreal

import os

app = FastAPI()

from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
DATABASE_USER = os.getenv("SURREALDB_USER")
DATABASE_PASS = os.getenv("SURREALDB_PASS")
DATABASE_NAMESPACE = os.getenv("SURREALDB_NAMESPACE")
DATABASE_NAME = os.getenv("SURREALDB_DATABASE")

import re


def convert_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%d.%m.%y, %H:%M:%S").isoformat()

@app.post("/")
async def create_log_entry():

    try: 
        with open('_chat_2.txt', 'r') as file:
            for line in file:
                cleaned_line = line.replace('\u200e', '').strip()
                # print(cleaned_line)

                # Regular expression to match the datetime and the message
                pattern = r"\[(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}:\d{2})\] (.*?): (.*)"
                match = re.match(pattern, cleaned_line)

                datetime_str = match.group(1)  # Extracted datetime
                message = match.group(3)        # Extracted message
                sender = match.group(2)         # Extracted sender            
                
                # Convert datetime to ISO format
                iso_datetime = convert_datetime(datetime_str)
                
                # Using a context manager to connect and disconnect
                with Surreal(DATABASE_URL) as db:
                    db.signin({"username": DATABASE_USER, "password": DATABASE_PASS})
                    db.use(DATABASE_NAMESPACE, DATABASE_NAME)

                    db.create(
                        "log_entry",
                        {
                            "created_at": iso_datetime,
                            "sender": sender,
                            "message": message,
                        },
                    )

                    print({"created_at": iso_datetime, "sender": sender, "message": message})

    except Exception as e:
        print(f"An Exception e happened: {e}")