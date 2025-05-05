from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# Set up WebDriver with user profile
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=C:/Users/Phil/AppData/Local/Google/Chrome/User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com/")

# Wait for WhatsApp Web to load
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "x1n2onr6._ak9y"))
)

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
    else: #write me selenium code to cick the single chats and get the chat history
        for chat in chat_elements:
            try:
                chat_name = chat.get_attribute("title")
                if chat_name not in seen_chats:
                    driver.execute_script("arguments[0].scrollIntoView(true);", chat)
                    time.sleep(0.5)  # Ensure the chat is in view
                    print("Scrolled to chat:", chat_name)
                    
                    driver.execute_script("arguments[0].click();", chat)
                    time.sleep(1)  # Allow the chat to open

                    # Retrieve chat history
                    chat_history = driver.find_elements(By.CSS_SELECTOR, "div.some-chat-history-class")  # Replace with actual class for chat messages
                    for message in chat_history:
                        print(message.text)  # Print each message in the chat history

                    seen_chats.add(chat_name)
            except Exception as e:
                print(f"Error processing chat: {e}")

    # Update seen chats
    seen_chats.update(current_chats)

    # Scroll down
    driver.execute_script("arguments[0].scrollBy(0, 1000);", chat_list)
    time.sleep(1)  # Allow chats to load

print("✅ Reached the last chat!")
driver.quit()
