import time

from selenium.webdriver.common.by import By

from whatsapp_handling.messages import collect_messages





async def iterate_chats(driver):

    print("Listing all chats... \n")
    
    # Find the element with aria-label="Chatliste"
    chat_list_element = driver.find_element(By.CSS_SELECTOR, '[aria-label="Chatliste"]')

    if chat_list_element:
        print("list_chats: Found Chatliste! \n")

    # Get all subelements (direct children)
    subelements = chat_list_element.find_elements(By.XPATH, './*')

    # Store in an array
    chat_list_subelements = []

    for n, element in enumerate(subelements):
        chat_list_subelements.append(element)

        print(f"Chat No {n}: ")

        # Try to find the element with class '_ak8n' at any depth under this chat element
        name_element = element.find_elements(By.CSS_SELECTOR, '.x1iyjqo2')
        chat_name = name_element[0].get_attribute('title')
        print(chat_name)

        # Try to find the element with class '_ak8i' at any depth under this chat element
        time_elements = element.find_elements(By.CSS_SELECTOR, '._ak8i')
        chat_time = time_elements[0].text
        print(chat_time)

        if ":" in chat_time:
            print("time is a time!")

            # Scroll to make element visible (like old_chat_reader.py)
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)
         
            # Check if clickable before clicking (like old_chat_reader.py)
            if element.is_displayed() and element.is_enabled():
                element.click()
                print(f"✅ Clicked on chat {n}: {chat_name} \n")

                await collect_messages(driver, chat_name)

            else:
                print(f"❌ Chat element not clickable for: {chat_name}")
    
            time.sleep(1)

        else:
            print("\n")
            continue


            
        
        n += 1

    print(f"list_chats: Found {len(chat_list_subelements)} subelements in the chat list")
    
    return chat_list_subelements