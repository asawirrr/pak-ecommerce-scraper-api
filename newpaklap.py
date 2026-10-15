# new_paklap.py

import requests
from bs4 import BeautifulSoup
import json
from requests.compat import urljoin
import re

def scrape_page(page_number, query, search_url):
    try:
        # Fetch the first page with the search parameters
        params = {'q': query, 'page': 1}
        response = requests.get(search_url, params=params)
    except requests.RequestException as e:
        print(f"Failed to retrieve page 1. Error: {e}")
        return None

    # If we are on a page greater than 1, modify the URL to add the page number
    if page_number > 1:
        try:
            # Get the base URL from the response and append page number
            base_url = response.url  # This gives the URL formed for the first page
            page_url = f"{base_url}&p={page_number}"

            # Make a new request for the specific page
            response = requests.get(page_url)
        except requests.RequestException as e:
            print(f"Failed to retrieve page {page_number}. Error: {e}")
            return None
    
    # Stop if we hit an error (non-200 status code)
    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code:", response.status_code)
        return None

    try:
        # Parse the HTML content of the search results page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <li> elements with class="item product product-item"
        li_elements = soup.find_all('li', class_='item product product-item')
    
        if not li_elements:
            return None
    except Exception as e:
        print(f"Error parsing page {page_number}: {e}")
        return None

    products = []
    
    for li in li_elements:
        try:
            # Find the anchor tag within the <li> element
            anchor = li.find('a', class_='product-item-link')
            
            # Compare the query with the text of the anchor tag
            if anchor and query.lower() in anchor.text.strip().lower():
                img_tag = li.find('img')
                
                if img_tag and anchor:  # Make sure both img and anchor are present
                    img_src = img_tag['src']
                    anchor_href = anchor['href']
                    
                    if not img_src.startswith('http'):
                        img_src = urljoin(search_url, img_src)
                    if not anchor_href.startswith('http'):
                        anchor_href = urljoin(search_url, anchor_href)
                    
                    # Extract old price
                    old_price_span = li.find('span', {'data-price-type': 'oldPrice'})
                    old_price = old_price_span.find('span', class_='price').get_text(strip=True) if old_price_span else 'No old price available'
                
                    # Extract final price
                    final_price_span = li.find('span', {'data-price-type': 'finalPrice'})
                    price = final_price_span.find('span', class_='price').get_text(strip=True) if final_price_span else 'No price available'
                
                    # Extract product title
                    product_title = anchor.get_text(strip=True) if anchor else 'No title available'
                    
                    product_sku = None
                    rating_value = "0"
                    rating_count = "0"
                    availability = "In Stock"
                    # Construct product info dictionary
                    
                    
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
            print(f"Error extracting product info: {e}")
            continue
    
    return products

def run_scraper(query):
    search_url = 'https://www.paklap.pk/catalogsearch/result/'
    all_products = []
    page_number = 1

    # Keep scraping until a non-200 status code is received
    while True:
        try:
            products = scrape_page(page_number, query, search_url)
        except Exception as e:
            print(f"Error scraping page {page_number}: {e}")
            break
        
        # If no products are returned, stop the loop
        if products is None:
            break
        
        all_products.extend(products)
        page_number += 1

    # Convert to JSON
    return json.dumps(all_products, indent=4)

if __name__ == '__main__':
    query = 'i7'  # You can change this to whatever you want to scrape
    output = run_scraper(query)
    print(output)
