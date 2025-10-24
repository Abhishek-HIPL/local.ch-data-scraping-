import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, \
    StaleElementReferenceException

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
    # print("Closed cookie popup")
    time.sleep(1)
except NoSuchElementException:
    print("No cookie popup found")



Top_categories=driver.find_element(By.XPATH,"//button[normalize-space()='Top categories']")
Top_categories.click()
time.sleep(3)






# Grab all top category elements
Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")

# Filter out unwanted links
Categories_from_A_to_Z = [
    cat for cat in Categories_from_A_to_Z
    if cat.get_attribute('href') not in ["/en/categories", "#"]
]




json_file = "data.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump([], f, ensure_ascii=False, indent=4)



for i in range(len(Categories_from_A_to_Z)):
    # Refetch the list every time to avoid StaleElementReferenceException
    Categories_from_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
    Categories_from_A_to_Z = [
        cat for cat in Categories_from_A_to_Z
        if cat.get_attribute('href') not in ["/en/categories", "#"]
    ]

    category = Categories_from_A_to_Z[i]
    category_name = category.text
    # print(f"Clicking category: {category_name}")

    # Click the category
    category.click()
    time.sleep(2)





    category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")

    for i in range(len(category_items)):
        # Refetch elements every iteration to avoid stale elements
        category_items = driver.find_elements(By.XPATH, "//div[@class='cz']//div//a")
        item = category_items[i]
        item_name = item.text
        print(f"Category: {item_name}")

        # Click the item
        item.click()
        time.sleep(2)

        # Now inside this item, get the A to Z elements
        inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
        # print(f"Found {len(inside_A_to_Z)} A–Z items")

        for i in range(len(inside_A_to_Z)):
            # Refetch elements each time to avoid stale references
            inside_A_to_Z = driver.find_elements(By.XPATH, "//div[@class='b4']//a")
            A_to_z = inside_A_to_Z[i]
            name = A_to_z.text
            # print(f"Clicking A–Z link: {name}")

            # Click the A–Z link
            A_to_z.click()


            # After clicking A–Z link
            time.sleep(2)  # wait for the page to load

            from selenium.common.exceptions import StaleElementReferenceException

            # Wait for the cities to load
            time.sleep(2)  # you can replace with WebDriverWait for better reliability

            try:
                all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
                for i in range(len(all_cities_for)):
                    # Refetch elements every iteration to avoid stale references
                    all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cA']//div//a")
                    city = all_cities_for[i]

                    try:
                        city_name = city.text
                        print(f"City: {city_name}")

                        # Click the city
                        city.click()
                        time.sleep(2)  # wait for page to load

                        professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")

                        for i in range(len(professionals)):
                            # Refetch elements in each loop to avoid stale element error
                            professionals = driver.find_elements(By.XPATH, "//div[@class='ly']//div//a")

                            profession = professionals[i]
                            profession_name = profession.text.strip() or f"Profession {i + 1}"
                            # print(f"Clicking on: {profession_name}")


                            try:
                                profession.click()


                                from selenium.webdriver.common.by import By
                                from selenium.webdriver.support.ui import WebDriverWait
                                from selenium.webdriver.support import expected_conditions as EC

                                try:
                                    # Wait up to 10 seconds for target section to appear
                                    target_section = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//div[@class='sd']"))
                                    )

                                    # Scroll smoothly into that section
                                    driver.execute_script(
                                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                        target_section
                                    )
                                    print(" Scrolled to the target section successfully!")
                                    time.sleep(2)
                                    title=driver.find_element(By.XPATH,"//div[@class='jt']//h1")
                                    print(f"Title:{title.text}")

                                    address_find=driver.find_element(By.XPATH,"//div[@class='qJ']//div//div")
                                    print(f"Address:{address_find.text}")

                                    # After breakfast

                                    try:
                                        Ratings = driver.find_element(By.XPATH,"//div[@class='rN']//div[@class='qk qn']")
                                        print(f"Rating:{Ratings.text}")
                                    except NoSuchElementException:
                                        print("Rating not yet")

                                    try:
                                        contact_section = driver.find_element(
                                            By.XPATH,
                                            "//section[@class='l:col l:border l:border-local-gray l:rounded-2xl l:p-4 l:break-words']//ul"
                                        )
                                        items = contact_section.find_elements(By.TAG_NAME, "li")

                                        email_value = None

                                        for item in items:
                                            text = item.text.strip()

                                            # Check for email
                                            if "@" in text:
                                                email_value = text.replace("E-Mail:", "").strip()

                                        # Print only email
                                        if email_value:
                                            print(f"Email:{email_value}")

                                    except NoSuchElementException:
                                        print("Contact info section not found.")


                                except Exception as e:
                                    print(f" Could not scroll to target section: {e}")

                                print("Opened URL:", driver.current_url)
                                time.sleep(3)  # wait 3 seconds on the new page
                                data_dict = {
                                    "category": item_name,
                                    "city": city_name,
                                    "title": title,
                                    "address": address_find,
                                    "rating": Ratings,
                                    "email": email_value,
                                    "url": driver.current_url
                                }

                                print(json.dumps(data_dict, ensure_ascii=False, indent=4))
                                print(f"data:{data_dict}")
                                # Append to JSON file
                                with open(json_file, "r+", encoding="utf-8") as f:
                                    data = json.load(f)
                                    data.append(data_dict)

                                    f.seek(0)
                                    json.dump(data, f, ensure_ascii=False, indent=4)
                            except Exception as e:
                                print(f" Could not click on : {e}")

                            # Go back and wait before next iteration
                            driver.back()
                            time.sleep(2)

                        # Scrape something on the city page if needed
                        # ...

                        # Go back to the previous page
                        driver.back()
                        time.sleep(2)

                    except StaleElementReferenceException:
                        # Retry once if the element went stale
                        all_cities_for = driver.find_elements(By.XPATH, "//div[@class='cI']//div//a")
                        city = all_cities_for[i]
                        city_name = city.text
                        print(f"(Retry) Clicking city: {city_name}")
                        city.click()
                        time.sleep(2)
                        driver.back()
                        time.sleep(2)

            except StaleElementReferenceException:
                print("Stale element, skipping this set of cities.")

            time.sleep(2)

            # You can scrape data here from the A–Z page if needed

            # Go back to previous page
            driver.back()
            time.sleep(2)

        # Go back to previous page to click next item
        driver.back()
        time.sleep(2)

        # driver.back()
        time.sleep(2)

    # Go back to main page
    driver.back()
    time.sleep(2)

driver.quit()

