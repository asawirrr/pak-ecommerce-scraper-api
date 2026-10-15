import requests
import re
import json
from bs4 import BeautifulSoup

def scrap_single_product(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')


    script_tags = soup.find_all('script', type='application/ld+json')
    raw_data = ''
    for script in script_tags:
        raw_data += script.string if script.string else ''

    # Use regular expression to find the ratingValue
    rating_value = 'No rating available'
    match = re.search(r'"ratingValue":\s*"(\d+\.\d+)"', raw_data)
    if match:
        rating_value = match.group(1)

    title_div = soup.find('div', class_='product__title')
    product_title = title_div.find('h1').get_text(strip=True) if title_div else 'No title available'

    product_sku = soup.find('p', class_='product__sku caption-with-letter-spacing')
    product_sku = product_sku.get_text(strip=True).replace('SKU:', '') if product_sku else 'No SKU available'

    price = soup.find('span', class_='price-item price-item--regular')
    price = price.get_text(strip=True) if price else 'No price available'

    media_div = soup.find('div', class_='product__media media media--transparent')
    image_tag = media_div.find('img') if media_div else None
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else 'No image available'

    product_info = {
        "Product URL": url,
        "Product Title": product_title,
        "Product SKU": product_sku,
        "Product Price": price,
        "Image URL": image_url,
        "Product Rating": rating_value
    }
    json_output = json.dumps(product_info, indent=4)

    return json_output

query = 'shirt'
base_url = 'https://www.elo.shopping/search'
page_number = 1

url = f'{base_url}?q={query}&page={page_number}'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

pagination = soup.find_all('a', class_='pagination__item link')
total_pages = int(pagination[-1].get_text(strip=True)) if pagination else 1

for page in range(1, total_pages + 1):
    url = f'{base_url}?q={query}&page={page}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', class_='full-unstyled-link')
    product_hrefs = [link.get('href') for link in links]
    product_hrefs = set(product_hrefs)

    for href in product_hrefs:
      url = 'https://www.elo.shopping'+href
      print(scrap_single_product(url))