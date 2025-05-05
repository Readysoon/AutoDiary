from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# Set up WebDriver with user profile
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=C:/Users/Phil/AppData/Local/Google/Chrome/User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com/")

wait = WebDriverWait(driver, 10)
elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listitem']")))

# Click on the second element
if len(elements) > 1:
    elements[2].click()
else:
    print("The second element is not available.")

time.sleep(500)

