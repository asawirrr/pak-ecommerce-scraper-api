# newelo.py

import requests
from bs4 import BeautifulSoup
import json
import re
from requests.compat import urljoin
from concurrent.futures import ThreadPoolExecutor

# URL of the website's search endpoint
search_url = 'https://www.elo.shopping/search'

def get_product(url, img_src):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching product URL {url}: {e}")
        return {}

    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        rating_value = "0"
        rating_count = "0"
        for script in script_tags:
            try:
                json_data = json.loads(script.string)
                if 'aggregateRating' in json_data:
                    rating_value = json_data['aggregateRating']['ratingValue']
                    rating_count = json_data['aggregateRating']['ratingCount']
                    break
            except (json.JSONDecodeError, KeyError):
                continue

        title_div = soup.find('div', class_='product__title')
        product_title = title_div.find('h1').get_text(strip=True) if title_div else 'No title available'

        product_sku = soup.find('p', class_='product__sku caption-with-letter-spacing')
        product_sku = product_sku.get_text(strip=True).replace('SKU:', '') if product_sku else 'No SKU available'

        price = soup.find('span', class_='price-item price-item--regular')
        price = price.get_text(strip=True) if price else 'No price available'

        old_price = soup.find('s', class_='price-item price-item--regular')
        old_price = old_price.get_text(strip=True) if old_price else 'No old price available'

        availability = "In Stock"
    except Exception as e:
        print(f"Error parsing product data from {url}: {e}")
        return {}
    
    
    
    # Clean price and old_price to allow only digits and commas, excluding any decimals
    price = re.sub(r'\.\d*|[^0-9,]', '', price)
    old_price = re.sub(r'\.\d*|[^0-9,]', '', old_price)

    product_info = {
        "Product URL": url,
        "Product Title": product_title,
        "Product SKU": product_sku,
        "Product Price": price,
        "Product Old Price": old_price,
        "Image URL": img_src,
        "Product Rating": rating_value,
        "Product Rating Count": rating_count,
        "Availability": availability
    }
    return product_info

def scrape_page(page_number, query):
    params = {'q': query, 'page': page_number}
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Check for HTTP request errors
    except requests.RequestException as e:
        print(f"Failed to retrieve page {page_number}. Error: {e}")
        return []

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        li_elements = soup.find_all('li', class_='grid__item')
        products = []

        for li in li_elements:
            img_tag = li.find('img')
            anchor_tag = li.find('a', class_='full-unstyled-link')
            
            if img_tag and anchor_tag:
                img_src = img_tag['src']
                anchor_href = anchor_tag['href']
                
                if not img_src.startswith('http'):
                    img_src = urljoin(search_url, img_src)
                if not anchor_href.startswith('http'):
                    anchor_href = urljoin(search_url, anchor_href)

                product_info = get_product(anchor_href, img_src)
                if product_info:
                    products.append(product_info)
    except Exception as e:
        print(f"Error parsing page {page_number}: {e}")
        return []

    return products

def run_scraper(query):
    page_numbers = [1, 2, 3, 4, 5]  # Specify the pages you want to scrape
    all_products = []
    
    # Use ThreadPoolExecutor to run the scrape_page function concurrently for each page
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda pn: scrape_page(pn, query), page_numbers))
    except Exception as e:
        print(f"Error during parallel scraping: {e}")

    # Flatten the results into a single list
    for result in results:
        for product in result:
            all_products.append(product)

    # Convert to JSON
    return json.dumps(all_products, indent=4)

if __name__ == '__main__':
    # Example usage:
    query = 'Shirt'  # You can change this to whatever you want to scrape
    output = run_scraper(query)
    print(output)
