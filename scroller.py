from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Set up WebDriver with user profile
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=C:/Users/Phil/AppData/Local/Google/Chrome/User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com/")

# Wait for WhatsApp Web to load
time.sleep(5)  # Adjust if needed

# Locate the chat list container
chat_list = driver.find_element(By.CLASS_NAME, "x1n2onr6._ak9y")

# Store unique chat names
seen_chats = set()

while True:
    # Find all chat name elements
    chat_elements = driver.find_elements(By.CLASS_NAME, "x1iyjqo2")

    # Extract chat names
    current_chats = {chat.get_attribute("title") for chat in chat_elements if chat.text.strip()}

    # Check if there are new chats
    if current_chats.issubset(seen_chats):  # If no new names, stop scrolling
        break

    # Update seen chats
    seen_chats.update(current_chats)

    # Scroll down
    driver.execute_script("arguments[0].scrollBy(0, 1000);", chat_list)
    time.sleep(1)  # Allow chats to load

print("✅ Reached the last chat!")
driver.quit()
