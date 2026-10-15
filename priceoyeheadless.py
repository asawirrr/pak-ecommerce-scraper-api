from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from requests.compat import urljoin
import time
import re
from bs4 import BeautifulSoup

def products_to_jsn(all_div_html_content, search_url, query):
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

            # Extract prices
            try:
                price = soup.find('div', class_='price-box').get_text(strip=True)
            except AttributeError:
                price = "Price not available"

            try:
                old_price = soup.find('div', class_='price-diff-retail').get_text(strip=True)
            except AttributeError:
                old_price = "Old Price not available"

            # Extract product title
            try:
                product_title = soup.find('div', class_='p-title').get_text(strip=True)
            except AttributeError:
                product_title = "Title not available"
                
            # Split the query into individual words
            query_words = query.lower().split()

            # Check if all query words exist in the product title
            if all(word in product_title.lower() for word in query_words):
                # Extract rating and review count
                try:
                    rating_value = soup.find('span', class_='h6 bold').get_text(strip=True)
                except AttributeError:
                    rating_value = "No rating available"

                try:
                    rating_count = soup.find('span', class_='rating-h7').get_text(strip=True)
                except AttributeError:
                    rating_count = "No rating count available"

            

                product_sku = None

                # Set default availability
                availability = "In Stock"

                # Check for availability based on ribbon classes
                if soup.find('mark', class_='ribbon_discontinued') or soup.find('mark', class_='ribbon_coming_soon'):
                    availability = "Out Of Stock"

            
                # Clean price and old_price to allow only digits and commas, excluding any decimals
                price = re.sub(r'\.\d*|[^0-9,]', '', price)
                old_price = re.sub(r'\.\d*|[^0-9,]', '', old_price)
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
        driver.get("https://www.priceoye.pk/")

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
            EC.presence_of_element_located((By.CLASS_NAME, "b-productBox"))
        )
    except Exception as e:
        print(f"Error during interaction with the website: {e}")




    count = 0
    all_products = []

    scroll_pause_time = 1
    scroll_increment = 300

    current_scroll_position = 0
    new_scroll_position = scroll_increment
    #scrolling down until the next page button is available in viewport
    while True:
        try:
            driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
            current_scroll_position = new_scroll_position
            new_scroll_position += scroll_increment
            time.sleep(scroll_pause_time)

            try:
                element = driver.find_element(By.ID, "next-button")
                is_in_viewport = driver.execute_script(
                    "var rect = arguments[0].getBoundingClientRect();"
                    "return (rect.top >= 0 && rect.bottom <= window.innerHeight);", element)

                if is_in_viewport:# element (next button) will never be in viewport in priceoye because its dynamically load more paging on single page
                    print("Element is in the viewport.")
                else:
                    print("Element is not in the viewport yet.")
            except Exception as e:
                print(f"Error encountered: {e}")




            scroll_height = driver.execute_script("return document.body.scrollHeight")
            count+=1
            if count==6:
                time.sleep(3)
            if count==10 or current_scroll_position >= scroll_height:# check if very much scrolling did or end pf page is appeared then scrape
                time.sleep(3)
                ('very much scrolling already OR Reached the bottom of the page.')
                div_elements = driver.find_elements(By.CLASS_NAME, "b-productBox")
                
                all_div_html_content = [element.get_attribute('outerHTML') for element in div_elements]
        
                products = products_to_jsn(all_div_html_content, search_url, query)
                all_products.extend(products)
                break
            
        except Exception as e:
            print(f"Error during scrolling: {e}")


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
    query = "samsung s22"
    result = run_scraper(query)
    if result is not None:
        print(result)
    else:
        print("No data scraped.")