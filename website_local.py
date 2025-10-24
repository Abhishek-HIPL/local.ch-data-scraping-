import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get("https://www.local.ch/en")
driver.maximize_window()
time.sleep(2)

# Close cookie popup if it exists
try:
    cookie_button = driver.find_element(By.XPATH, "//button[contains(@class,'ot-sdk-btn') or contains(text(),'Accept')]")
    cookie_button.click()
    time.sleep(1)
except NoSuchElementException:
    print("No cookie popup found")

# Open Top categories
try:
    top_categories = driver.find_element(By.XPATH, "//button[normalize-space()='Top categories']")
    top_categories.click()
    time.sleep(2)
except NoSuchElementException:
    print("Top categories button not found")
    driver.quit()
    exit()

# Prepare JSON file
json_file = "data2.json"
if not os.path.exists(json_file):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# Grab all top category elements
Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
Categories_from_A_to_Z = [
    cat for cat in Categories_from_A_to_Z if cat.get_attribute('href') not in ["/en/categories", "#"]
]

for cat_idx in range(len(Categories_from_A_to_Z)):
    # Refetch categories to avoid stale reference
    Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
    Categories_from_A_to_Z = [
        cat for cat in Categories_from_A_to_Z if cat.get_attribute('href') not in ["/en/categories", "#"]
    ]
    category = Categories_from_A_to_Z[cat_idx]
    category_name = category.text
    category.click()
    time.sleep(2)

    # Category items
    category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")
    for item_idx in range(len(category_items)):
        category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")
        item = category_items[item_idx]
        item_name = item.text
        item.click()
        time.sleep(2)

        # Inside A-Z
        inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
        for a2z_idx in range(len(inside_A_to_Z)):
            inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
            a2z_item = inside_A_to_Z[a2z_idx]
            a2z_name = a2z_item.text
            a2z_item.click()
            time.sleep(2)

            # Cities
            try:
                all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
                for city_idx in range(len(all_cities_for)):
                    all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
                    city = all_cities_for[city_idx]
                    city_name = city.text
                    city.click()
                    time.sleep(2)

                    # Professionals
                    professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")
                    for prof_idx in range(len(professionals)):
                        professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")
                        prof = professionals[prof_idx]
                        prof_name = prof.text.strip() or f"Profession {prof_idx+1}"
                        try:
                            prof.click()
                            time.sleep(2)

                            # Wait for target section
                            try:
                                target_section = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//div[@class='sd']"))
                                )
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                    target_section
                                )
                                time.sleep(1)
                            except:
                                print("Target section not found")

                            # Scrape details
                            title = driver.find_element(By.XPATH, "//div[@class='jt']//h1").text
                            address = driver.find_element(By.XPATH, "//div[@class='qJ']//div//div").text

                            try:
                                rating = driver.find_element(By.XPATH, "//div[@class='rN']//div[@class='qk qn']").text
                            except NoSuchElementException:
                                rating = None

                            try:
                                contact_section = driver.find_element(
                                    By.XPATH,
                                    "//section[@class='l:col l:border l:border-local-gray l:rounded-2xl l:p-4 l:break-words']//ul"
                                )
                                email_value = None
                                for item in contact_section.find_elements(By.TAG_NAME, "li"):
                                    text = item.text.strip()
                                    if "@" in text:
                                        email_value = text.replace("E-Mail:", "").strip()
                                        break
                            except NoSuchElementException:
                                email_value = None

                            # Prepare dict
                            data_dict = {
                                "category": item_name,
                                "A_to_Z": a2z_name,
                                "city": city_name,
                                "title": title,
                                "address": address,
                                "rating": rating,
                                "email": email_value,
                                "url": driver.current_url
                            }

                            print(json.dumps(data_dict, ensure_ascii=False, indent=4))

                            # Append to JSON safely
                            if os.path.getsize(json_file) > 0:
                                with open(json_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                            else:
                                data = []

                            data.append(data_dict)

                            with open(json_file, "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)

                        except Exception as e:
                            print(f"Could not click professional: {e}")
                        driver.back()
                        time.sleep(2)

                    driver.back()
                    time.sleep(2)

            except StaleElementReferenceException:
                print("Stale element in cities, skipping")

            driver.back()
            time.sleep(2)

        driver.back()
        time.sleep(2)

    driver.back()
    time.sleep(2)

driver.quit()
