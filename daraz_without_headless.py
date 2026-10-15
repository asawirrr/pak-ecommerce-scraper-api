from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from requests.compat import urljoin
import time


from bs4 import BeautifulSoup

def products_to_jsn(all_div_html_content, search_url):
    products = []
    for div_html in all_div_html_content:
        try:
            # Parse the div_html string into a BeautifulSoup object
            soup = BeautifulSoup(div_html, 'html.parser')
            
            # Find anchor and img elements safely
            anchor = soup.find('a')
            img = soup.find('img')

            # Set default values in case elements are not found
            img_src = 'Image not available'
            anchor_href = 'URL not available'

            if img and 'src' in img.attrs:
                img_src = img['src']
                if not img_src.startswith('http'):
                    img_src = urljoin(search_url, img_src)

            if anchor and 'href' in anchor.attrs:
                anchor_href = anchor['href']
                if not anchor_href.startswith('http'):
                    anchor_href = urljoin(search_url, anchor_href)

            old_price = 'No old price available'

            # Extract final price
            try:
                price = soup.find('span', class_='ooOxS').get_text(strip=True)
            except AttributeError:
                price = "Price not available"

            # Find the div with class 'RfADt'
            product_div = soup.find('div', class_='RfADt')

            # Now, find the anchor tag inside the found div
            if product_div:
                anchor = product_div.find('a')
                # Get the text of the anchor tag
                product_title = anchor.get_text(strip=True) if anchor else 'No title available'
            else:
                product_title = 'No title available'

            product_sku = None

            # Find the rating div (adjust selector if needed)
            rating_div = soup.find('div', class_='mdmmT _32vUv')
            if rating_div:
                rating_elements = rating_div.find_all('i', class_='_9-ogB Dy1nx')
                rating_count = len(rating_elements)

                # Map the count to the correct rating
                rating_map = {1: 1.5, 2: 2.5, 3: 3.5, 4: 4.5, 5: 5.0}
                rating_value = rating_map.get(rating_count, "Unknown Rating")
            else:
                rating_value = "No rating available"

            try:
                rating_count = soup.find('span', class_='qzqFw').get_text(strip=True)
            except AttributeError:
                rating_count = "No rating count available"

            availability = "In Stock"

            # Construct product info dictionary
            product_info = {
                "Product URL": anchor_href,
                "Product Title": product_title,
                "Product SKU": product_sku,
                "Product Price": price,
                "Product Old Price": old_price,
                "Image URL": img_src,
                "Product Rating": rating_value,
                "Product Rating Count": rating_count,
                "Availability": availability
            }
            products.append(product_info)

        except Exception as e:
            print(f"Error processing product: {e}")

    return products

# Set up Chrome driver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Open Daraz website
driver.get("https://www.daraz.pk/")

# Set the search URL for later use
search_url = driver.current_url

# Wait for the search bar to load and interact with it
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.NAME, "q"))
)

# Search for 'catfood Fluffy'
input_element = driver.find_element(By.NAME, "q")
input_element.clear()
input_element.send_keys("catfood Fluffy" + Keys.ENTER)

time.sleep(5)

# Wait for search results to load
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "Bm3ON"))
)


all_products = []
second_page = False

# Scroll the page gradually in increments
scroll_pause_time = 1  # Pause between scrolls (1 second)
scroll_increment = 300  # Pixels to scroll down each time

# Get the current scroll height of the page
current_scroll_position = 0
new_scroll_position = scroll_increment

while True:
    driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
    current_scroll_position = new_scroll_position
    new_scroll_position += scroll_increment
    time.sleep(scroll_pause_time)

    try:
        # Find the pagination button with class 'ant-pagination-item-link'
        element = driver.find_element(By.CLASS_NAME, "ant-pagination-item-link")
        is_in_viewport = driver.execute_script(
            "var rect = arguments[0].getBoundingClientRect();"
            "return (rect.top >= 0 && rect.bottom <= window.innerHeight);", element)

        if is_in_viewport:
            is_disabled = element.get_attribute('aria-disabled') == 'true' or 'ant-pagination-disabled' in element.get_attribute('class')
            if not is_disabled:
                print("Element is in the viewport and not disabled. Clicking the element.")

                div_elements = driver.find_elements(By.CLASS_NAME, "Bm3ON")
                all_div_html_content = [element.get_attribute('outerHTML') for element in div_elements]

                products = products_to_jsn(all_div_html_content, search_url)
                all_products.extend(products)
                my_button = driver.find_element(By.CLASS_NAME, "ant-pagination-item-2")
                my_button.click()
                second_page = True
                break
            else:
                print("Element is in the viewport but disabled.")
        else:
            print("Element is not in the viewport yet.")

    except Exception as e:
        print(f"Error encountered: {e}")

    scroll_height = driver.execute_script("return document.body.scrollHeight")
    if current_scroll_position >= scroll_height:
        print("Reached the bottom of the page.")
        break

if second_page:
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "Bm3ON")))
    current_scroll_position = 0
    new_scroll_position = scroll_increment

    while True:
        driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
        current_scroll_position = new_scroll_position
        new_scroll_position += scroll_increment
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if current_scroll_position >= scroll_height:
            break

    div_elements = driver.find_elements(By.CLASS_NAME, "Bm3ON")
    all_div_html_content = [element.get_attribute('outerHTML') for element in div_elements]
    products = products_to_jsn(all_div_html_content, search_url)
    all_products.extend(products)

json_output = json.dumps(all_products, indent=4)
print(json_output)

driver.quit()
