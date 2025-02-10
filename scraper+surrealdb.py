from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging
import surrealdb as Surreal

# SurrealDB connection
DB_URL = "http://localhost:8000"
DB_USER = "root"
DB_PASS = "password"  # Use the correct password
DB_NAMESPACE = "test"  # Set this to any valid namespace
DB_DATABASE = "test"  # Set this to any valid database

async def get_db():
    try:
        logging.info(f"Attempting to connect to {DB_URL}")
        db = Surreal(DB_URL)
        logging.info(f"Created SurrealDB instance")

        await db.connect()
        db.signin({
            "user": DB_USER,
            "pass": DB_PASS,
            "NS": DB_NAMESPACE,  # Explicitly set namespace
            "DB": DB_DATABASE     # Explicitly set database
        })

    except Exception as e:
        print(f"DB connection error: {e}")  # Avoid exposing credentials
        raise


# Start Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=./chrome_data")  # Keep session
driver = webdriver.Chrome(options=options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com")
input("Press Enter after scanning the QR code...")

def scrape_chats():
    messages = driver.find_elements(By.CSS_SELECTOR, "div.copyable-text")
    for msg in messages:
        text = msg.find_element(By.CSS_SELECTOR, "span.selectable-text").text
        metadata = msg.get_attribute("data-pre-plain-text")
        
        if metadata:
            timestamp, sender = metadata.strip("[]").split("] ", 1)
            
            # Save to SurrealDB
            db.create("messages", {
                "timestamp": timestamp,
                "sender": sender.strip(": "),
                "text": text
            })
            print(f"Saved: {sender}: {text} ({timestamp})")

# Run the scraper
while True:
    scrape_chats()
    time.sleep(5)  # Adjust as needed

driver.quit()
