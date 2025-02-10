from selenium import webdriver
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()

# Set a persistent user data directory
options.add_argument("--user-data-dir=C:/Users/Phil/AppData/Local/Google/Chrome/User Data")  # Path to Chrome user data
options.add_argument("--profile-directory=Default")  # Use your main Chrome profile

# Start WebDriver with the profile
driver = webdriver.Chrome(options=options)

driver.get("https://web.whatsapp.com/")

time.sleep(500)

element = driver.find_element(By.CLASS_NAME, "x1qlqyl8")
print(element.text)

# Find all message elements
messages = driver.find_elements(By.CLASS_NAME, "copyable-text")

'''
for message in messages:
    # Extract data from 'data-pre-plain-text' attribute
    raw_text = message.get_attribute("data-pre-plain-text")  # Example: "[14:53, 9.2.2025] Phil: "
    
    if raw_text:
        # Extract time, date, and sender
        raw_text = raw_text.strip("[]")  # Remove brackets
        time_date, sender = raw_text.split("] ")  # Split at "] "
        time, date = time_date.split(", ")  # Split time and date
        sender = sender.strip(":")  # Remove colon

        # Extract message text
        message_text = message.find_element(By.CLASS_NAME, "_ao3e").text

        print(f"Date: {date}, Time: {time}, Sender: {sender}, Message: {message_text}")

'''

print("iterated through all messages")

time.sleep(5)

driver.quit()