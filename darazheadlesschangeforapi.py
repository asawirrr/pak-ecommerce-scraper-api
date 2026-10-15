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
            soup = BeautifulSoup(div_html, 'html.parser')
            anchor = soup.find('a')
            img = soup.find('img')

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

            try:
                price = soup.find('span', class_='ooOxS').get_text(strip=True)
            except AttributeError:
                price = "Price not available"

            product_div = soup.find('div', class_='RfADt')
            if product_div:
                anchor = product_div.find('a')
                product_title = anchor.get_text(strip=True) if anchor else 'No title available'
            else:
                product_title = 'No title available'

            product_sku = None

            rating_div = soup.find('div', class_='mdmmT _32vUv')
            if rating_div:
                rating_elements = rating_div.find_all('i', class_='_9-ogB Dy1nx')
                rating_count = len(rating_elements)
                rating_map = {1: 1.5, 2: 2.5, 3: 3.5, 4: 4.5, 5: 5.0}
                rating_value = rating_map.get(rating_count, "Unknown Rating")
            else:
                rating_value = "No rating available"

            try:
                rating_count = soup.find('span', class_='qzqFw').get_text(strip=True)
            except AttributeError:
                rating_count = "No rating count available"

            availability = "In Stock"

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







def run_scraper(query):
    # Set up Chrome driver in headless mode
    try:
        service = Service(executable_path="chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode (no GUI) makes browser invisible
        options.add_argument('--disable-gpu')  # Disable GPU (optional, recommended for headless)
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems in Linux containers
        options.add_argument('--window-size=1920,1080')  # Set a window size for consistency
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error setting up the Chrome driver: {e}")







    try:
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
        input_element.send_keys(query + Keys.ENTER)

        time.sleep(5)

        # Wait for search results to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Bm3ON"))
        )
    except Exception as e:
        print(f"Error during interaction with the website: {e}")





    all_products = []
    second_page = False

    scroll_pause_time = 1
    scroll_increment = 300

    current_scroll_position = 0
    new_scroll_position = scroll_increment
    #scrolling down until the 2nd page button is available in viewport
    while True:
        try:
            driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
            current_scroll_position = new_scroll_position
            new_scroll_position += scroll_increment
            time.sleep(scroll_pause_time)

            try:
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
        except Exception as e:
            print(f"Error during scrolling: {e}")



    # if second page was found then scroll down to load images
    if second_page:
        try:
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
        except Exception as e:
            print(f"Error on the second page: {e}")

    try:
        json_output = json.dumps(all_products, indent=4)
        #print(json_output)
        return json_output
    except Exception as e:
        print(f"Error serializing products to JSON: {e}")
        return None  # Return None if there's an error in the scraping process

    # Close the browser
    finally:
        driver.quit()

# Main function for standalone execution
if __name__ == "__main__":
    query = "catfood Fluffy"
    result = run_scraper(query)
    if result is not None:
        print(result)
    else:
        print("No data scraped.")