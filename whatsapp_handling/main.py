import time
import json


from whatsapp_handling.chats import iterate_chats


from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Wait for the chat list to load
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# handle login and use helper functions to collect todays chats
def collect_todays_messages():

    # Set up Chrome options to persist login session
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=./chrome_profile")  # Persist user data
    chrome_options.add_argument("--profile-directory=Default")       # Use default profile

    driver = webdriver.Chrome(options=chrome_options)

    # Whatsapp muss erst hier gestartet werden um zu schauen ob man eingelogt ist
    driver.get("http://web.whatsapp.com/")

    while True:
        if "Steps to log in" in driver.page_source or "Schritte zum Anmelden" in driver.page_source:

            print("Please log in ...")

            time.sleep(30)

            # hier die Chance geben, einzuloggen und danach Seite im while loop nochmal neu laden
            driver.get("http://web.whatsapp.com/")

        elif "Chats" or "WhatsApp" in driver.page_source:

            print("Logged in! \n")

            # sleep for some time to let chats load!
            time.sleep(7)

            # go through all chats
            today_chats = iterate_chats(driver)
            
            print(f"\nFound {len(today_chats)} chats used today!")

            break

        else:

            print("Probably loading or some error ...")

            time.sleep(5)
# 
