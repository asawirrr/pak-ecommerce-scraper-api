# new_priceoye.py

import requests
from bs4 import BeautifulSoup
import json
from requests.compat import urljoin
from concurrent.futures import ThreadPoolExecutor

def get_product(url, img_src):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the response was not successful
    except requests.RequestException as e:
        print(f"Failed to retrieve product details from {url}. Error: {e}")
        return None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the rating value
        rating_value_div = soup.find('div', class_='semi-bold rating-points')
        rating_value = rating_value_div.get_text(strip=True) if rating_value_div else 'No rating available'

        # Get the rating count (extract only the number from the string like "100 Ratings")
        rating_count_div = soup.find('div', class_='semi-bold rating-count')
        rating_count = rating_count_div.get_text(strip=True).split()[0] if rating_count_div else 'No rating count available'

        # Get availability
        availability_div = soup.find('span', class_='summary-price text-black bold stock-status')
        availability = availability_div.get_text(strip=True) if availability_div else 'No availability information'

        # Get product title (check both title_div and h3)
        title_div = soup.find('div', class_='product-title')
        product_title = title_div.find('h3', class_='h2').get_text(strip=True) if title_div and title_div.find('h3') else 'No title available'

        # Get SKU
        product_sku_div = soup.find('p', class_='product__sku caption-with-letter-spacing')
        product_sku = product_sku_div.get_text(strip=True).replace('SKU:', '').strip() if product_sku_div else 'No SKU available'

        # Get price (extract the number part only)
        price_div = soup.find('span', class_='summary-price text-black price-size-lg bold')
        price = ''.join(filter(str.isdigit, price_div.get_text())) if price_div else 'No price available'

        # Get old price (extract the number part only)
        old_price_div = soup.find('span', class_='summary-price line-through stock-info')
        old_price = ''.join(filter(str.isdigit, old_price_div.get_text())) if old_price_div else 'No old price available'

        # Create the product info dictionary
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
    except Exception as e:
        print(f"Error parsing product details from {url}: {e}")
        return None

def scrape_page(page_number, query, search_url):
    try:
        params = {'q': query, 'page': page_number}
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an HTTPError if the response was not successful
    except requests.RequestException as e:
        print(f"Failed to retrieve page {page_number}. Error: {e}")
        return []

    try:
        # Parse the HTML content of the search results page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all div elements with class 'productBox b-productBox'
        product_boxes = soup.find_all('div', class_='productBox b-productBox')

        if not product_boxes:
            return None  # Stops when no product boxes are found
    except Exception as e:
        print(f"Error parsing page {page_number}: {e}")
        return []

    products = []
    for box in product_boxes:
        try:
            # Find all amp-img tags within the product box and replace them with img tags
            amp_images = box.find_all('amp-img')
            anchor_tag = box.find('a')
            anchor_href = anchor_tag['href']
            img_src = None
            for amp_img in amp_images:
                img_src = amp_img.get('src')
                # If the image source is a relative URL, convert it to an absolute URL
                if img_src and not img_src.startswith('http'):
                    img_src = urljoin(search_url, img_src)

            product_info = get_product(anchor_href, img_src)
            if product_info:  # Only append if product_info is not None
                products.append(product_info)
        except Exception as e:
            print(f"Error processing product box: {e}")
            continue

    return products

def run_scraper(query):
    search_url = 'https://priceoye.pk/search'
    all_products = []
    page_numbers = [1, 2]  # Page numbers to scrape

    # Using ThreadPoolExecutor to scrape pages concurrently
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda p: scrape_page(p, query, search_url), page_numbers))

        # Collect all results
        for result in results:
            if result:
                all_products.extend(result)

        # Return the JSON output
        return json.dumps(all_products, indent=4)
    except Exception as e:
        print(f"Error during concurrent scraping: {e}")
        return None

if __name__ == '__main__':
    query = 'Oppo'  # You can change this to whatever you want to scrape
    output = run_scraper(query)
    print(output)
