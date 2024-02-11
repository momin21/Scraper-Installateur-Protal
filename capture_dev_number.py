from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

with open('scrapper-configs.json') as config_file:
    config = json.load(config_file)

# Extract variables from config
username = config.get('username')
password = config.get('password')
main_page_url = config.get('main_page_url')
fileName = config.get('fileName')
devNumberFileName = config.get('devNumberFileName')
chromedriver_path = config.get('chromedriver_path')
endingDevNumber = 999920164

# Init driver
driver = webdriver.Chrome(executable_path=chromedriver_path)
# Go to the main page
driver.get(main_page_url)

WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-textfield email')))
username_field = driver.find_element_by_name("username")
password_field = driver.find_element_by_name("password")
username_field.send_keys(username)
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)

# Wait for main table page to load
WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-app-loading')))
print("Installateur Loaded")

# Get the table
table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-table-table')))

header_element = driver.find_element_by_css_selector(".v-table-caption-container.v-table-caption-container-align-center")
header_element.click()
time.sleep(2)
header_element.click()
time.sleep(2)

last_height = driver.execute_script("return document.body.scrollHeight")
devNumberSet = set()
try:
     while True:
       rows = table.find_elements_by_tag_name('tr')
       for row in rows:
         devNumberSet.add(row.find_elements_by_tag_name('td')[0].text)
         
       ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
       time.sleep(2)
       table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-table-table')))
       print("Dev Numbers Captured so far: ", len(devNumberSet))
       
except Exception as e:
  print(e)

print("Total Dev Numbers found: ", len(devNumberSet))
try:
  devNumbers = list(devNumberSet)
  with open(devNumberFileName, 'w') as file:
    json.dump(devNumbers, file)

  print("Dev Numbers saved in file: ", devNumberFileName)

except Exception as e:
  print(e)
  print("Error saving dev number to file: ", devNumberFileName)