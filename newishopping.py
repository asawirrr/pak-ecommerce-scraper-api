# new_ishopping.py

import requests
from bs4 import BeautifulSoup
import json
from requests.compat import urljoin
from concurrent.futures import ThreadPoolExecutor
import re

# URL of the website's search endpoint
search_url = 'https://www.ishopping.pk/catalogsearch/result/'

def scrape_page(page_number, query):
    try:
        params = {'q': query, 'p': page_number}  # Assuming the pagination param is 'p'
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Failed to retrieve page {page_number}. Error: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product elements
        items = soup.find_all('div', class_='product-item-info')
        products = []

        for item in items:
            try:
                # Extract product title
                img_tag = item.find('img')
                anchor_tag = item.find('a', class_='product-item-link')
                
                
                product_title = anchor_tag.get_text(strip=True) if anchor_tag else 'No title available'
                
                # Split the query into individual words
                query_words = query.lower().split()

                # Check if all query words exist in the product title
                if all(word in product_title.lower() for word in query_words):

                    # Extract image and product link
                    if img_tag and anchor_tag:
                        img_src = img_tag['src']
                        anchor_href = anchor_tag['href']

                        if not img_src.startswith('http'):
                            img_src = urljoin(search_url, img_src)
                        if not anchor_href.startswith('http'):
                            anchor_href = urljoin(search_url, anchor_href)

                    # Extract old price
                    old_price_span = item.find('span', {'data-price-type': 'oldPrice'})
                    old_price = old_price_span.find('span', class_='price').get_text(strip=True) if old_price_span else 'No old price available'

                    # Extract final price
                    final_price_span = item.find('span', {'data-price-type': 'finalPrice'})
                    price = final_price_span.find('span', class_='price').get_text(strip=True) if final_price_span else 'No price available'


                    # Placeholder for SKU and rating (you may want to extract these too)
                    product_sku = None
                    rating_value = "0"
                    rating_count = "0"
                    availability = "In Stock"

                
                
                    # Clean price and old_price to allow only digits and commas, excluding any decimals
                    price = re.sub(r'\.\d*|[^0-9,]', '', price)
                    old_price = re.sub(r'\.\d*|[^0-9,]', '', old_price)
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
                print(f"Error extracting product info: {e}")
                continue

        return products

    except Exception as e:
        print(f"Error parsing page {page_number}: {e}")
        return []

def run_scraper(query):
    page_numbers = [1, 2, 3]  # Specify the pages you want to scrape
    all_products = []
    
    # Use ThreadPoolExecutor to scrape multiple pages concurrently
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(lambda pn: scrape_page(pn, query), page_numbers))
    except Exception as e:
        print(f"Error during concurrent scraping: {e}")

    # Flatten the results into a single list
    for result in results:
        all_products.extend(result)

    # Convert to JSON
    return json.dumps(all_products, indent=4)

if __name__ == '__main__':
    query = 'shirt'  # You can change this to whatever you want to scrape
    output = run_scraper(query)
    print(output)
