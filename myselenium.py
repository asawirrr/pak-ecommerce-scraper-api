from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
service = Service('/path/to/chromedriver')

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the website's search endpoint
search_url = 'https://www.daraz.pk/catalog/'

# Search query
query = 'dispenser'

# Navigate to the search page
driver.get(search_url + '?q=' + query)

# Wait for page to load
time.sleep(5)  # Adjust based on your needs; more complex sites may require longer

# Get page source
html_content = driver.page_source

# Write the HTML content to a file
file_path = 'search_results.html'
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Close the browser
driver.quit()

# Open the HTML file in the default web browser
webbrowser.open(f'file://{os.path.realpath(file_path)}')
