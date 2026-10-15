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

# API route to scrape product info
@app.route('/elo/product', methods=['GET'])
def get_product_info():
    # Get the query parameter from the request URL
    url = request.args.get('query')
    
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    
    # Scrape the product info using the provided URL
    product_info = scrape_product(url)
    
    # Return the product info as JSON
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(debug=True)
