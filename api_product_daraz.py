from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
# http://127.0.0.1:5000/daraz/product?query=https://www.daraz.pk/products/-i269527731-s2240671572.html?scm=1007.51657.380827.0&pvid=131351ff-50ce-45d6-a6db-8852a3b389fa&search=flashsale&spm=a2a0e.tm80335142.FlashSale.d_269527731
app = Flask(__name__)

def run_scraper(url):
    # Set up Chrome driver in headless mode
    try:
        service = Service(executable_path="chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode (no GUI)
        options.add_argument('--disable-gpu')  # Disable GPU
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems in Linux containers
        options.add_argument('--window-size=1920,1080')  # Set a window size for consistency
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error setting up the Chrome driver: {e}")
        return None

    try:
        # Open product page
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp-block"))
        )
    except Exception as e:
        print(f"Error during interaction with the website: {e}")
        driver.quit()
        return None

    price = "Price not available"
    old_price = "Old price not available"
    availability = "Availability unknown"

    try:
        # Scroll down to ensure the price section is visible
        scroll_pause_time = 1
        scroll_increment = 300
        current_scroll_position = 0
        new_scroll_position = scroll_increment

        while True:
            # Try to find price element
            try:
                price_div = driver.find_element(By.CLASS_NAME, "pdp-product-price")
                is_in_viewport = driver.execute_script(
                    "var rect = arguments[0].getBoundingClientRect();"
                    "return (rect.top >= 0 && rect.bottom <= window.innerHeight);", price_div)
                
                if is_in_viewport:
                    # Check if price is available
                    span_price = price_div.find_element(By.TAG_NAME, "span")
                    if span_price:
                        price = span_price.text.strip()
                    # Try to find old price
                    old_price_div = price_div.find_element(By.CLASS_NAME, "origin-block")
                    if old_price_div:
                        old_price_span = old_price_div.find_element(By.CLASS_NAME, "pdp-price_type_deleted")
                        if old_price_span:
                            old_price = old_price_span.text.strip()
                    break
                else:
                    # Scroll down if not in viewport
                    driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
                    current_scroll_position = new_scroll_position
                    new_scroll_position += scroll_increment
                    time.sleep(scroll_pause_time)

                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    if current_scroll_position >= scroll_height:
                        print("Reached the bottom of the page, price not found.")
                        break
            except Exception as e:
                print(f"Error finding price: {e}")
                break

    except Exception as e:
        print(f"Error during scrolling for price: {e}")

    try:
        # Scroll down to find availability status
        while True:
            try:
                warning = driver.find_element(By.CLASS_NAME, "quantity-content-warning")
                availability = "Out of Stock"
                break
            except:
                try:
                    default = driver.find_element(By.CLASS_NAME, "quantity-content-default")
                    availability = "In Stock"
                    break
                except:
                    # Scroll down if not found
                    driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
                    current_scroll_position = new_scroll_position
                    new_scroll_position += scroll_increment
                    time.sleep(scroll_pause_time)

                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    if current_scroll_position >= scroll_height:
                        print("Reached the bottom of the page, availability not found.")
                        break

    except Exception as e:
        print(f"Error during scrolling for availability: {e}")

    # Collect product information
    product_info = {
        "Product Price": price,
        "Product Old Price": old_price,
        "Availability": availability
    }

    # Convert to JSON
    try:
        product_json = json.dumps(product_info, indent=4)
    except Exception as e:
        print(f"Error converting product information to JSON: {e}")
        product_json = None

    # Close the browser
    finally:
        driver.quit()

    return product_json

@app.route('/daraz/product', methods=['GET'])
def daraz_product():
    # Get the URL query parameter
    url = request.args.get('query')
    
    if not url:
        return jsonify({"error": "No query URL provided"}), 400

    # Call the scraper function
    result = run_scraper(url)

    if result:
        return jsonify(json.loads(result))
    else:
        return jsonify({"error": "Failed to scrape data"}), 500

if __name__ == "__main__":
    app.run(debug=True)
