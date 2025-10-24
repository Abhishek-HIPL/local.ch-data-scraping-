import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup ---
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

driver.get("https://www.local.ch/en")
driver.maximize_window()
time.sleep(2)

# Close cookie popup
try:
    cookie_button = driver.find_element(By.XPATH, "//button[contains(@class,'ot-sdk-btn') or contains(text(),'Accept')]")
    cookie_button.click()
    time.sleep(1)
except NoSuchElementException:
    pass

# Click Top Categories
Top_categories = driver.find_element(By.XPATH,"//button[normalize-space()='Top categories']")
Top_categories.click()
time.sleep(3)

# Grab all top category elements
Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
Categories_from_A_to_Z = [cat for cat in Categories_from_A_to_Z if cat.get_attribute('href') not in ["/en/categories", "#"]]

# Prepare JSON file
json_file = "data.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump([], f, ensure_ascii=False, indent=4)

# --- Main loop ---
for i in range(len(Categories_from_A_to_Z)):
    Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
    Categories_from_A_to_Z = [cat for cat in Categories_from_A_to_Z if cat.get_attribute('href') not in ["/en/categories", "#"]]

    category = Categories_from_A_to_Z[i]
    category_name = category.text
    category.click()
    time.sleep(2)

    category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")
    for j in range(len(category_items)):
        category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")
        item = category_items[j]
        item_name = item.text
        item.click()
        time.sleep(2)

        inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
        for k in range(len(inside_A_to_Z)):
            inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
            A_to_z = inside_A_to_Z[k]
            az_name = A_to_z.text
            A_to_z.click()
            time.sleep(2)

            all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
            for l in range(len(all_cities_for)):
                all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
                city = all_cities_for[l]
                city_name = city.text
                city.click()
                time.sleep(2)

                professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")
                for m in range(len(professionals)):
                    professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")
                    profession = professionals[m]
                    profession_name = profession.text.strip() or f"Profession {m + 1}"
                    profession.click()
                    time.sleep(2)

                    try:
                        # Scrape info
                        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='jt']//h1")))
                        title = driver.find_element(By.XPATH,"//div[@class='jt']//h1").text
                        address = driver.find_element(By.XPATH,"//div[@class='qJ']//div//div").text

                        try:
                            rating = driver.find_element(By.XPATH,"//div[@class='rN']//div[@class='qk qn']").text
                        except NoSuchElementException:
                            rating = None

                        try:
                            contact_section = driver.find_element(By.XPATH, "//section[@class='l:col l:border l:border-local-gray l:rounded-2xl l:p-4 l:break-words']//ul")
                            items = contact_section.find_elements(By.TAG_NAME, "li")
                            email_value = None
                            for item_el in items:
                                text = item_el.text.strip()
                                if "@" in text:
                                    email_value = text.replace("E-Mail:", "").strip()
                        except NoSuchElementException:
                            email_value = None

                        # Save data in dictionary
                        data_dict = {
                            "category": category_name,
                            "sub_item": item_name,
                            "A-Z": az_name,
                            "city": city_name,
                            "professional": profession_name,
                            "title": title,
                            "address": address,
                            "rating": rating,
                            "email": email_value,
                            "url": driver.current_url
                        }

                        # Print dictionary as JSON immediately
                        print(json.dumps(data_dict, ensure_ascii=False, indent=4))

                        # Append to JSON file
                        with open(json_file, "r+", encoding="utf-8") as f:
                            data = json.load(f)
                            data.append(data_dict)
                            f.seek(0)
                            json.dump(data, f, ensure_ascii=False, indent=4)

                    except Exception as e:
                        print(f"Error scraping {profession_name}: {e}")

                    driver.back()
                    time.sleep(2)

                driver.back()
                time.sleep(2)

            driver.back()
            time.sleep(2)

        driver.back()
        time.sleep(2)

    driver.back()
    time.sleep(2)

driver.quit()
print("✅ Scraping completed. All data saved to data.json")
