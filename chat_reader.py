import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# INSERT_YOUR_CODE
from selenium.webdriver.common.by import By

# Wait for the chat list to load
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options to persist login session
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=./chrome_profile")  # Persist user data
chrome_options.add_argument("--profile-directory=Default")       # Use default profile

driver = webdriver.Chrome(options=chrome_options)

driver.get("http://web.whatsapp.com/")

def gatter_chats():
    print("Starting to collect messages...")

    # Wait a bit for messages to load
    time.sleep(3)

    # Scroll up to make sure we can see the "Heute" separator
    print("Scrolling to see more of the chat history...")
    driver.execute_script("window.scrollTo(0, -1000);")
    time.sleep(2)

    # Look for "Heute" separator first across the entire page
    print("Looking for 'Heute' separator...")
    all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
    heute_found = False
    heute_element = None

    for element in all_elements:
        try:
            if element.text.strip().lower() == "heute":
                heute_found = True
                heute_element = element
                print(f"Found 'Heute' separator: {element.text}")
                break
        except:
            continue

    if not heute_found:
        print("No 'Heute' separator found in the visible area")
        # Try to scroll more and look again
        driver.execute_script("window.scrollTo(0, -2000);")
        time.sleep(2)
        
        for element in all_elements:
            try:
                if element.text.strip().lower() == "heute":
                    heute_found = True
                    heute_element = element
                    print(f"Found 'Heute' separator after scrolling: {element.text}")
                    break
            except:
                continue

    # Scroll to bottom to ensure all recent messages are loaded
    print("Scrolling to bottom to load all recent messages...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Get all message containers with multiple approaches
    print("Finding message containers...")
    message_selectors = [
        "[data-testid='msg-container']",
        "div[data-testid*='message']", 
        ".message-in, .message-out",
        "div[role='row']",
        "div._akbu",
        "div._amjv",  # Another WhatsApp message class
        "div[class*='message']"  # Any div with 'message' in class name
    ]

    all_containers = []
    for selector in message_selectors:
        containers = driver.find_elements(By.CSS_SELECTOR, selector)
        if containers:
            print(f"Found {len(containers)} containers with selector: {selector}")
            all_containers.extend(containers)

    # Remove duplicates by keeping unique elements
    message_containers = []
    seen_elements = set()
    for container in all_containers:
        try:
            # Use element location and text as identifier to avoid duplicates
            identifier = (container.location['x'], container.location['y'], container.text.strip()[:50])
            if identifier not in seen_elements:
                seen_elements.add(identifier)
                message_containers.append(container)
        except:
            continue

    print(f"Total unique message containers found: {len(message_containers)}")

    if not message_containers:
        print("No message containers found!")
        return []

    collected_messages = []

    # If we found "Heute", only collect messages that come after it in the DOM
    if heute_found and heute_element:
        print("Collecting only messages after 'Heute' separator...")
        
        # Get the position of the "Heute" element
        heute_location = heute_element.location['y']
        
        for i, container in enumerate(message_containers):
            try:
                # Check if this message comes after the "Heute" separator
                container_location = container.location['y']
                
                print(f"Container {i}: location={container_location}, heute_location={heute_location}")
                print(f"Container {i} text preview: {container.text.strip()[:100]}")
                
                # Only process messages that appear BELOW (after) the "Heute" separator
                if container_location <= heute_location:
                    print(f"Skipping container {i} - it's before 'Heute'")
                    continue  # Skip messages that are above "Heute"
                
                print(f"Processing container {i} - it's after 'Heute'")
                
                # Extract message data
                message_data = {}
                container_text = container.text.strip()

                # Get sender name from the specific structure
                sender_elements = container.find_elements(By.CSS_SELECTOR, "span._ahxt, span._ao3e")
                for elem in sender_elements:
                    elem_text = elem.text.strip()
                    # Look for sender names (usually not timestamps and contain letters)
                    if elem_text and not elem_text.replace(":", "").replace(".", "").isdigit() and len(elem_text) > 2:
                        # Skip if it's a time pattern
                        if not (len(elem_text) == 5 and ":" in elem_text):
                            message_data['sender'] = elem_text
                            break

                # Also try data-pre-plain-text attribute for sender
                if not message_data.get('sender'):
                    pre_plain_elements = container.find_elements(By.CSS_SELECTOR, "[data-pre-plain-text]")
                    for elem in pre_plain_elements:
                        pre_text = elem.get_attribute("data-pre-plain-text")
                        if pre_text and "]" in pre_text and ":" in pre_text:
                            # Extract sender from pattern like "[15:33, 21.9.2025] Simon : "
                            sender_part = pre_text.split("] ")[-1].split(" :")[0].strip()
                            if sender_part:
                                message_data['sender'] = sender_part
                                break

                # Get message text from selectable-text spans
                message_text_selectors = [
                    "span.selectable-text",
                    "span._ao3e.selectable-text", 
                    ".copyable-text span.selectable-text",
                    "span._ao3e"
                ]

                for sel in message_text_selectors:
                    text_elements = container.find_elements(By.CSS_SELECTOR, sel)
                    for text_elem in text_elements:
                        elem_text = text_elem.text.strip()
                        # Skip if it looks like a timestamp or sender name
                        if (elem_text and 
                            not (len(elem_text) == 5 and ":" in elem_text) and  # Not a time like "15:33"
                            elem_text != message_data.get('sender', '') and     # Not the sender name
                            len(elem_text) > 3):                               # Has meaningful content
                            message_data['text'] = elem_text
                            break
                    if message_data.get('text'):
                        break

                # Fallback to container text if no specific text found
                if not message_data.get('text') and container_text:
                    # Clean up container text by removing sender and time
                    clean_text = container_text
                    if message_data.get('sender'):
                        clean_text = clean_text.replace(message_data['sender'], '').strip()
                    # Remove common time patterns
                    import re
                    clean_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', clean_text).strip()
                    if clean_text and len(clean_text) > 3:
                        message_data['text'] = clean_text

                # Get timestamp from multiple possible locations
                time_patterns = [
                    "span.x1c4vz4f",           # Based on your HTML
                    "span.x1rg5ohu",           # Another time pattern from your HTML
                    "[data-testid='msg-meta'] span",
                    "span"
                ]
                
                for pattern in time_patterns:
                    time_elements = container.find_elements(By.CSS_SELECTOR, pattern)
                    for elem in time_elements:
                        elem_text = elem.text.strip()
                        # Look for time pattern HH:MM
                        if elem_text and ":" in elem_text and len(elem_text) == 5:
                            try:
                                # Validate it's actually a time
                                hours, minutes = elem_text.split(":")
                                if 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59:
                                    message_data['time'] = elem_text
                                    break
                            except:
                                continue
                    if message_data.get('time'):
                        break

                # Only add if we got meaningful text
                if message_data.get('text') and len(message_data['text']) > 0:
                    collected_messages.append(message_data)
                    print(f"Collected message: {message_data['text'][:50]}...")

            except Exception as e:
                print(f"Error processing container {i}: {e}")
                continue
    else:
        print("'Heute' separator not found - collecting only the last message")
        # If no "Heute" found, just collect the last message (most recent)
        if message_containers:
            container = message_containers[-1]  # Last message (most recent)
            message_data = {}
            container_text = container.text.strip()

            # Get message text
            for sel in ["span.selectable-text", "div.selectable-text", ".copyable-text span", "span"]:
                text_elements = container.find_elements(By.CSS_SELECTOR, sel)
                if text_elements and text_elements[0].text.strip():
                    message_data['text'] = text_elements[0].text.strip()
                    break

            if not message_data.get('text') and container_text:
                message_data['text'] = container_text

            if message_data.get('text'):
                collected_messages.append(message_data)

    print(f"\nCollected {len(collected_messages)} messages from today:")
    for i, msg in enumerate(collected_messages, 1):
        print(f"{i}. Sender: {msg.get('sender', 'Unknown')}")
        print(f"   Time: {msg.get('time', 'Unknown')}")
        print(f"   Text: {msg.get('text', 'No text')}")
        print("-" * 50)

    return collected_messages




def list_chats():
    """List all chats and identify which ones were used today"""
    print("Listing all chats...")
    
    # Wait for chats to load
    time.sleep(2)
    
    # Get all chat list items
    chat_list_selectors = [
        "div[role='listitem']",
        "div._ak8q",
        "div[data-testid*='list-item']"
    ]
    
    all_chats = []
    for selector in chat_list_selectors:
        chats = driver.find_elements(By.CSS_SELECTOR, selector)
        if chats:
            print(f"Found {len(chats)} chats with selector: {selector}")
            all_chats = chats
            break
    
    if not all_chats:
        print("No chats found!")
        return []
    
    today_chats = []
    all_chat_info = []
    
    for i, chat in enumerate(all_chats):
        try:
            chat_info = {}
            
            # Get chat name
            name_selectors = [
                "span[title]",
                "span._ao3e[title]",
                ".x1iyjqo2.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1rg5ohu.x1jchvi3.xjb2p0i.xo1l8bm.x17mssa0.x1ic7a3i._ao3e"
            ]
            
            for selector in name_selectors:
                name_elements = chat.find_elements(By.CSS_SELECTOR, selector)
                if name_elements:
                    chat_name = name_elements[0].get_attribute("title") or name_elements[0].text.strip()
                    if chat_name and len(chat_name) > 0:
                        chat_info['name'] = chat_name
                        break
            
            # Get last message time
            time_selectors = [
                "div._ak8i",
                ".x1iyjqo2.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1rg5ohu._ao3e"
            ]
            
            for selector in time_selectors:
                time_elements = chat.find_elements(By.CSS_SELECTOR, selector)
                if time_elements:
                    time_text = time_elements[0].text.strip()
                    if time_text:
                        chat_info['last_message_time'] = time_text
                        break
            
            # Get last message preview
            message_selectors = [
                "span.x1iyjqo2.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1rg5ohu._ao3e",
                "div._ak8k span"
            ]
            
            for selector in message_selectors:
                message_elements = chat.find_elements(By.CSS_SELECTOR, selector)
                if message_elements:
                    # Get the last span which usually contains the message text
                    for elem in reversed(message_elements):
                        msg_text = elem.text.strip()
                        if msg_text and len(msg_text) > 3 and msg_text != chat_info.get('name', ''):
                            chat_info['last_message'] = msg_text[:100] + ("..." if len(msg_text) > 100 else "")
                            break
                    if chat_info.get('last_message'):
                        break
            
            # Determine if this chat was used today
            # Today's chats have timestamps like "16:08", "15:33" instead of "Gestern" or dates
            is_today = False
            if 'last_message_time' in chat_info:
                time_text = chat_info['last_message_time']
                # Check if it's a time format (HH:MM)
                if ":" in time_text and len(time_text) <= 6 and not any(word in time_text.lower() for word in ['gestern', 'yesterday', 'heute', 'today']):
                    try:
                        # Try to parse as time
                        time_parts = time_text.split(":")
                        if len(time_parts) == 2 and time_parts[0].isdigit() and time_parts[1].isdigit():
                            hours = int(time_parts[0])
                            minutes = int(time_parts[1])
                            if 0 <= hours <= 23 and 0 <= minutes <= 59:
                                is_today = True
                    except:
                        pass
            
            chat_info['is_today'] = is_today
            chat_info['index'] = i
            
            if chat_info.get('name'):  # Only add chats with names
                all_chat_info.append(chat_info)
                if is_today:
                    today_chats.append(chat_info)
                    
        except Exception as e:
            print(f"Error processing chat {i}: {e}")
            continue
    
    # Print results
    print(f"\n=== ALL CHATS ({len(all_chat_info)}) ===")
    for chat in all_chat_info:
        status = "📅 TODAY" if chat['is_today'] else "⏰ OLDER"
        print(f"{chat['index']:2d}. {status} | {chat.get('name', 'Unknown')}")
        print(f"    Time: {chat.get('last_message_time', 'Unknown')}")
        print(f"    Last: {chat.get('last_message', 'No message')}")
        print("-" * 60)
    
    print(f"\n=== TODAY'S ACTIVE CHATS ({len(today_chats)}) ===")
    for chat in today_chats:
        print(f"{chat['index']:2d}. {chat.get('name', 'Unknown')} - {chat.get('last_message_time', 'Unknown')}")
        print(f"    Last: {chat.get('last_message', 'No message')}")
        print("-" * 40)
    
    return today_chats

def iterate_chats():
        # Try multiple selectors for chat list items
    chat_selectors = [
        "div[data-testid*='list-item']",  # Any element with list-item in data-testid
        "div[role='listitem']",           # Chat items often have listitem role
        "[data-testid='cell-frame-container']",  # Original selector
        "div._ak8q",                      # WhatsApp's chat container class (may change)
        "div[title]",                     # Chat items usually have titles
    ]

    clicked = False
    for selector in chat_selectors:
        print(f"Trying selector: {selector}")
        try:
            chat_list = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            if chat_list and len(chat_list) >= 2:
                # Skip the first chat (archive) and click on the second chat
                try:
                    second_chat = chat_list[1]  # Index 1 = second chat
                    if second_chat.is_displayed() and second_chat.is_enabled():
                        second_chat.click()
                        print(f"Successfully clicked on SECOND chat using selector: {selector}")
                        # Wait for messages to load after clicking
                        
                        messages = gatter_chats()

                        print(messages)

                        time.sleep(1000)
                        clicked = True
                        break
                except Exception as chat_error:
                    print(f"Error clicking second chat with {selector}: {chat_error}")
                    continue
            elif chat_list:
                print(f"Only found {len(chat_list)} chat(s) with selector {selector}, need at least 2")
            else:
                print(f"No elements found for selector: {selector}")
                
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    if not clicked:
        print("Could not click on any chat. Please manually click on a chat.")

    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='msg-container']")

    print(messages)

    time.sleep(4)



time.sleep(3)

if "Steps to log in" in driver.page_source:
    print("Please log in ...")

else:
    print("Logged in!")

    # List all chats and identify today's active ones
    today_chats = list_chats()
    
    print(f"\nFound {len(today_chats)} chats used today!")

    time.sleep(100)
    
    # Continue with iterating through chats
    iterate_chats()

time.sleep(1)