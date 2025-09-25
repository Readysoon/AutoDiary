import time
import re
import pytz

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Create timezone object for Innsbruck
innsbruck_tz = pytz.timezone('Europe/Vienna')  # Austria uses Vienna timezone

# Parse your WhatsApp time and make it timezone-aware
def parse_whatsapp_time_with_tz(time_str):

    clean_str = time_str.strip("[]")
    time_part, date_part = clean_str.split(", ")    
    # Parse as naive datetime first
    dt_naive = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%Y %H:%M")
    
    # Make it timezone-aware (localize to Innsbruck time)
    dt_tz = innsbruck_tz.localize(dt_naive)
    
    return dt_tz.isoformat() 


def collect_messages(driver, chat_name):

    time.sleep(5)

    chat_window = driver.find_element(By.CSS_SELECTOR, '.x3psx0u.xwib8y2.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q')

    chat_window_subelements = chat_window.find_elements(By.XPATH, './*')

    # Iterate from the bottom element to the top
    for n, element in enumerate(reversed(chat_window_subelements)):

        # print(f"element No: {n}")
        element_class = element.get_attribute('class')
        # print(f"element class: {element_class}")

        # Try to extract the message text, sender, and time from the pre-plain-text attribute
        try:
            # Find the div with class 'copyable-text' inside this element
            copyable_text_div = element.find_element(By.CSS_SELECTOR, ".copyable-text")
            pre_plain_text = copyable_text_div.get_attribute("data-pre-plain-text")
            # Example: [16:09, 24.9.2025] Lukas Pördli:
            message_text = ""
            # The actual message text is inside a span with class '_ao3e selectable-text copyable-text'
            try:
                message_span = copyable_text_div.find_element(By.CSS_SELECTOR, "span._ao3e.selectable-text.copyable-text")
                message_text = message_span.text
            except Exception:
                message_text = ""
            if pre_plain_text:
                
                # print(f"element sender/time: {pre_plain_text.strip()}")

                bracket_content = re.search(r"\[.*?\]", pre_plain_text)
                # if bracket_content:
                #     print(f"Bracketed time: {bracket_content.group(0)}")

                # Extract the name (without the colon) after the bracketed time
                # Example: "[10:14, 24.9.2025] Phil:"
                name_match = re.search(r"\] (.*?):", pre_plain_text)
                name = name_match.group(1) if name_match else ""

                # print(f"Name: {name}")

                bracket_content_w_group = bracket_content.group(0)

                iso_time = parse_whatsapp_time_with_tz(bracket_content_w_group)

                # print(f"ISO time: {iso_time}")

                # print(f"element message: {message_text.strip()}\n")

                print(f"----- \n Chat Name: {chat_name} \n Sender: {name} \n Time: {iso_time} \n Nachricht: {message_text.strip()} \n -------")

            else:
                # fallback if no pre-plain-text
                text = element.text
#                 if text.strip():
#                     print(f"element text: \n{text}\n")
#                 else:
#                     print("element text: (no text)")
        except Exception:
            # fallback if no copyable-text div
            text = element.text
            if text.strip():
                print(f"element text: \n{text}\n")
            else:
                print("element text: (no text)")

        # Check if the element has all expected classes for the date separator and text is "Heute"
        expected_class = "x141l45o x1h3r9g6 x1hx0egp x78zum5 x1q0g3np xl56j7k xcytdqz"
        expected_classes = set(expected_class.split())
        element_classes = set(element_class.split())

        if expected_classes.issubset(element_classes) and text.strip() == "Heute":
            print("Found Heute within a date separator! \n")
            break

        





    