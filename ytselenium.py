from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.daraz.pk/")

# wait for 10 seconds like so the page get loaded and all the elements exist in the page (Best works with slow internet)
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.NAME, "q"))
)

input_element = driver.find_element(By.NAME, "q")
# clear if anything already written in search bar/element
input_element.clear()
input_element.send_keys("catfood Fluffy" + Keys.ENTER)


WebDriverWait(driver, 20).until(
     EC.presence_of_element_located((By.CLASS_NAME, "Bm3ON"))
)


# Find all elements with class name "Bm3ON"
div_elements = driver.find_elements(By.CLASS_NAME, "Bm3ON")

# Extract the HTML content of all found elements
all_div_html_content = [element.get_attribute('outerHTML') for element in div_elements]

# Optionally, write all HTML content to a file
file_path = 'search_results.html'
with open(file_path, 'w', encoding='utf-8') as file:
    for div_html in all_div_html_content:
        file.write(div_html + '\n')

time.sleep(10)

# Close the browser
driver.quit()

# Open the HTML file in the default web browser
webbrowser.open('search_results.html')




# # wait for 10 seconds like so the page get loaded and all the elements exist in the page (Best works with slow internet)
# WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Fluffy"))
# )


# after search results are shown find link containing text here Fluffy
# link = driver.find_element(By.PARTIAL_LINK_TEXT, "Fluffy")
# link.click()

# after search results are shown find link with exact text here Fluffy
# link = driver.find_element(By.LINK_TEXT, "Fluffy")
# link.click()

# after search results are shown if you want to find multiple links containing text here Fluffy
# it will return array
# links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Fluffy")
# link.click()



# to see otherwise the action will happen and the window will be closed quickly, sleep for 10 seconds
# time.sleep(10)
# driver.quit()