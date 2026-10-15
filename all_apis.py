from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import json
import time
import darazheadlesschangeforapi
import newelo
import newishopping
import newpaklap
import newpriceoye

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes







# Code 1 - Daraz Product Scraper
def run_scraper_daraz(url):
    try:
        service = Service(executable_path="chromedriver.exe")
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error setting up the Chrome driver: {e}")
        return None

    try:
        driver.get(url)
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

    finally:
        driver.quit()
    # Collect product information
    product_info = {
        "Product Price": price,
        "Product Old Price": old_price,
        "Availability": availability
    }

    return product_info

@app.route('/daraz/product', methods=['GET'])
def daraz_product():
    url = request.args.get('query')
    if not url:
        return jsonify({"error": "No query URL provided"}), 400
    result = run_scraper_daraz(url)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to scrape data"}), 500
    
    
    
    
    
    
    
    
    
    
    

# Code 2 - Elo Product Scraper
def scrape_product_elo(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during requests to {url}: {e}"}

    try:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product price
        price = soup.find('span', class_='price-item price-item--regular')
        price = price.get_text(strip=True) if price else 'No price available'

        # Extract old price
        old_price = soup.find('s', class_='price-item price-item--regular')
        old_price = old_price.get_text(strip=True) if old_price else 'No old price available'

        # Check product availability (defaulting to 'In Stock')
        availability = "In Stock"

        # Store the product info in a dictionary
        product_info = {
            "Product Price": price,
            "Product Old Price": old_price,
            "Availability": availability
        }

        return product_info
    
    except Exception as e:
        return {"error": f"Error scraping the product page: {e}"}

@app.route('/elo/product', methods=['GET'])
def get_product_info_elo():
    url = request.args.get('query')
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    product_info = scrape_product_elo(url)
    return jsonify(product_info)











# Code 3 - iShopping Product Scraper
def run_scraper_ishopping(url):
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

    return product_info

@app.route('/ishopping/product', methods=['GET'])
def ishopping_product():
    url = request.args.get('query')
    if not url:
        return jsonify({"error": "No query URL provided"}), 400
    result = run_scraper_ishopping(url)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to scrape data"}), 500










# Code 4 - PakLap Product Scraper
def scrape_product_paklap(url):
    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during requests to {url}: {e}"}

    try:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Try to find the price in the 'special-price' class
        try:
            price_container = soup.find('span', class_='special-price')
            price = price_container.find('span', class_='price').get_text(strip=True)
            print(price)
        except AttributeError:
            price = "Price not available"

        # Try to find the old price in the 'old-price' class
        try:
            old_price_container = soup.find('span', class_='old-price')
            old_price = old_price_container.find('span', class_='price').get_text(strip=True)
        except AttributeError:
            old_price = "Old price not available"
            
        if price == "Price not available":
            try:
                price_container = soup.find('span', class_='price-container price-final_price tax weee')
                price = price_container.find('span', class_='price').get_text(strip=True)
            except AttributeError:
                price = "Price not available"

        # Check product availability (defaulting to 'In Stock')
        availability = "In Stock"

        # Store the product info in a dictionary
        product_info = {
            "Product Price": price,
            "Product Old Price": old_price,
            "Availability": availability
        }

        return product_info
    
    except Exception as e:
        return {"error": f"Error scraping the product page: {e}"}

@app.route('/paklap/product', methods=['GET'])
def get_product_info_paklap():
    url = request.args.get('query')
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    product_info = scrape_product_paklap(url)
    return jsonify(product_info)










# Code 5 - PriceOye Product Scraper
def scrape_product_priceoye(url):
    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during requests to {url}: {e}"}

    try:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get availability
        try:
            availability_div = soup.find('span', class_='summary-price text-black bold stock-status')
            availability = availability_div.get_text(strip=True) if availability_div else 'No availability information'
        except Exception as e:
            availability = "Error fetching availability"

        # Get price
        try:
            price_div = soup.find('span', class_='summary-price text-black price-size-lg bold')
            price = ''.join(filter(str.isdigit, price_div.get_text())) if price_div else 'No price available'
        except Exception as e:
            price = "Error fetching price"

        # Get old price
        try:
            old_price_div = soup.find('span', class_='summary-price line-through stock-info')
            old_price = ''.join(filter(str.isdigit, old_price_div.get_text())) if old_price_div else 'No old price available'
        except Exception as e:
            old_price = "Error fetching old price"

        # Store the product info in a dictionary
        product_info = {
            "Product Price": price,
            "Product Old Price": old_price,
            "Availability": availability
        }

        return product_info
    
    except Exception as e:
        return {"error": f"Error scraping the product page: {e}"}

@app.route('/priceoye/product', methods=['GET'])
def get_product_info_priceoye():
    url = request.args.get('query')
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    product_info = scrape_product_priceoye(url)
    return jsonify(product_info)
















@app.route('/daraz', methods=['GET'])
def scrape_daraz():
    try:
        # Get the query parameter from the request
        query = request.args.get('query')  # Default value if no query is provided
        if not query:
            return jsonify({"error": "No query URL provided"}), 400
        
        # Call the run_scraper function with the query parameter
        json_output = darazheadlesschangeforapi.run_scraper(query)
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    



@app.route('/elo', methods=['GET'])
def scrape_elo():
    # Get the query parameter from the request
    query = request.args.get('query')
    
    if not query:  # Check if the query is provided
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Run the scraper with the given query
        json_output = newelo.run_scraper(query)  # Call the modified function
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500








@app.route('/ishopping', methods=['GET'])
def scrape_ishopping():
    # Get the query parameter from the request
    query = request.args.get('query')
    
    if not query:  # Check if the query is provided
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Run the scraper with the given query
        json_output = newishopping.run_scraper(query)  # Call the modified function
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@app.route('/paklap', methods=['GET'])
def scrape_paklap():
    # Get the query parameter from the request
    query = request.args.get('query')
    
    if not query:  # Check if the query is provided
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Run the scraper with the given query
        json_output = newpaklap.run_scraper(query)  # Call the modified function
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/priceoye', methods=['GET'])
def scrape_priceoye():
    # Get the query parameter from the request
    query = request.args.get('query')
    
    if not query:  # Check if the query is provided
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        # Run the scraper with the given query
        json_output = newpriceoye.run_scraper(query)  # Call the modified function
        
        # Return the JSON output as the Flask response
        return json_output, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
    
if __name__ == "__main__":
    app.run(debug=True)
