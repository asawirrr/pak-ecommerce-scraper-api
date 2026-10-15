from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

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
            EC.presence_of_element_located((By.CLASS_NAME, "title"))
        )

        time.sleep(5)  # Let the page load completely

        price = "Price not available"
        old_price = "Old price not available"
        availability = "Availability unknown"

        # Implement viewport scroll for price and old price
        scroll_pause_time = 1
        scroll_increment = 300
        current_scroll_position = 0
        new_scroll_position = scroll_increment

        while True:
            try:
                # Try to find the current price using ID
                price_element = driver.find_element(By.ID, "product-price-undefined")
                is_in_viewport = driver.execute_script(
                    "var rect = arguments[0].getBoundingClientRect();"
                    "return (rect.top >= 0 && rect.bottom <= window.innerHeight);", price_element)

                if is_in_viewport:
                    price = price_element.text.strip()  # Store the current price
                    # Try to find the old price using class name
                    old_price_element = driver.find_element(By.CLASS_NAME, "price-wrapper")
                    old_price = old_price_element.text.strip()  # Store the old price
                    break
                else:
                    # Scroll down if price not in viewport
                    driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
                    current_scroll_position = new_scroll_position
                    new_scroll_position += scroll_increment
                    time.sleep(scroll_pause_time)

                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    if current_scroll_position >= scroll_height:
                        print("Reached the bottom of the page, price not found.")
                        break
            except Exception as e:
                print(f"Error finding price or old price: {e}")
                break

        # Implement viewport scroll for availability
        while True:
            try:
                # Try to check availability by looking for the button
                availability_button = driver.find_element(By.CLASS_NAME, "is-button.add-cart-button")
                is_in_viewport = driver.execute_script(
                    "var rect = arguments[0].getBoundingClientRect();"
                    "return (rect.top >= 0 && rect.bottom <= window.innerHeight);", availability_button)

                if is_in_viewport:
                    button_text = availability_button.text.strip()
                    if "Add to Cart" in button_text:
                        availability = "In Stock"
                    elif "Coming Soon" in button_text:
                        availability = "Out of Stock"
                    break
                else:
                    # Scroll down if availability not in viewport
                    driver.execute_script(f"window.scrollTo({current_scroll_position}, {new_scroll_position});")
                    current_scroll_position = new_scroll_position
                    new_scroll_position += scroll_increment
                    time.sleep(scroll_pause_time)

                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    if current_scroll_position >= scroll_height:
                        print("Reached the bottom of the page, availability status not found.")
                        break
            except Exception as e:
                print(f"Error finding availability: {e}")
                break

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()

    # Check if old_price and price are the same, if so, set old_price to an empty string
    try:
        if old_price == price:
            old_price = ""
    except Exception as e:
        print(f"Error comparing price and old price: {e}")

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

    return product_json

@app.route('/ishopping/product', methods=['GET'])
def ishopping_product():
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
