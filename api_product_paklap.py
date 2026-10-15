from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Function to scrape a single product page and return product info
def scrape_product(url):
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

# API route to scrape product info
@app.route('/paklap/product', methods=['GET'])
def get_product_info():
    # Get the query parameter from the request URL
    url = request.args.get('query')  # Expecting 'url' as the parameter
    
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    
    # Scrape the product info using the provided URL
    product_info = scrape_product(url)
    
    # Return the product info as JSON
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(debug=True)
