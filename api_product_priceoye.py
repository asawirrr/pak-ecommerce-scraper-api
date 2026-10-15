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

# API route to scrape product info
@app.route('/priceoye/product', methods=['GET'])
def get_product_info():
    # Get the query parameter from the request URL
    url = request.args.get('query')  # Expecting 'query' as the parameter
    
    if not url:
        return jsonify({"error": "No product URL provided."}), 400
    
    # Scrape the product info using the provided URL
    product_info = scrape_product(url)
    
    # Return the product info as JSON
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(debug=True)
