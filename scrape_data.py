from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd

with open('scrapper-configs.json') as config_file:
    config = json.load(config_file)

# Extract variables from config
username = config.get('username')
password = config.get('password')
main_page_url = config.get('main_page_url')
fileName = config.get('fileName')
devNumberFileName = config.get('devNumberFileName')
chromedriver_path = config.get('chromedriver_path')

with open(devNumberFileName) as devNumberFile:
  devNumbers = json.load(devNumberFile)

print("Count of Dev Numbers to be processed: ", len(devNumbers))

# Init driver
driver = webdriver.Chrome(executable_path=chromedriver_path)

# Login
driver.get(main_page_url)
WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-textfield email')))
username_field = driver.find_element_by_name("username")
password_field = driver.find_element_by_name("password")
username_field.send_keys(username)
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)
# Wait for main table page to load
WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-app-loading')))
print("Login Done")

scrapedData = []
count = 0

def closeTab():
  driver.close()
  driver.switch_to.window(driver.window_handles[0])
  
def openNewTab():
  driver.execute_script("window.open('');")
  driver.switch_to.window(driver.window_handles[1])
  driver.get(main_page_url)
  WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-app-loading')))
  WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-table-table')))

def searchDevNumber(devNumber):
  print("Scrapping info for: ", devNumber)
  try:
    number_input = driver.find_element(By.CLASS_NAME, "meinsenec-searchfield")
    number_input.clear()
    number_input.send_keys(devNumber)
    number_input.send_keys(Keys.ENTER)
    time.sleep(2)
    table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-table-table')))
    rows = table.find_elements_by_tag_name("tr")
    print(len(rows), " rows found againts ", devNumber)
    return rows[0] if len(rows) > 0 else None

  except Exception as e:
    print(e)
    print("Search failed / observing record after searching failed")
    return None

def isRowClickable(entry):
  first_column = entry.find_element_by_xpath(".//td[1]")
  return "v-table-cell-content-meinsenec-padlock-wrench" not in first_column.get_attribute("class")

def appendValues(installations, besitzer, akku):
    scrapedData.append({
                    'Installation': installations.get('Installation'),
                    'Installationsdatum': installations.get('Installationsdatum'),
                    'Name': besitzer.get('Name'),
                    'Firma': besitzer.get('Firma'),
                    'Ort': besitzer.get('Ort'),
                    'E-Mail': besitzer.get('E-Mail'),
                    'Straße': besitzer.get('Straße'),
                    'Telefon': besitzer.get('Telefon'),
                    'Anzahl Module': akku.get('Anzahl Module'),
                    'Kapazität': akku.get('Kapazität')
                })
    print("Scrapped Data for customers so far: ", len(scrapedData))

def scrapeDataForCustomer():
    installations = getTableValues('Installation')
    besitzer = getTableValues('Name')
    akku = getTableValues('Technologie')
    appendValues(installations, besitzer, akku)

def commitDataToFile():
    try:
        print("Committing Data to " + fileName )
        df = pd.DataFrame(scrapedData)
        df.to_excel(fileName, index=False)
        print("Data pushed successfully")
    except Exception as e:
        print("Data not pushed successfully", e)
        
def getTableValues(tableName):
    installation_table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//table[.//span[text()="'+ tableName +'"]]')))
    print("table: "+ tableName +" Found")
    values_dict = {}
    dataRows = installation_table.find_elements(By.TAG_NAME, 'tr')

    for row in dataRows:
        caption = row.find_element(By.CLASS_NAME, 'v-formlayout-captioncell').find_element(By.TAG_NAME, 'span').text.strip()
        value = row.find_element(By.CLASS_NAME, 'v-formlayout-contentcell').find_element(By.TAG_NAME, 'div').text.strip()
        values_dict[caption] = value
    return values_dict

def scrapeData():
  WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'v-tabsheet-tabsheetpanel')))
  scrapeDataForCustomer()
  time.sleep(2)
  
def clickOnRecord(entry):
  try:
    if isRowClickable(entry):
      entry.click()
      scrapeData()
    else:
      print("Skipping the row with paddle lock")
  except Exception as e:
    print(e)
    print("Sub table not found after click")
  return


for devNumber in devNumbers:
  count += 1
  print("Iteration # ", count)

  try:
    # open new tab
    openNewTab()
    entry = searchDevNumber(devNumber)
    # Search the dev Number
    if entry:
      # Scrape the row info
      clickOnRecord(entry)
    else:
      print("No Entry found against: ", devNumber)
      continue

    closeTab()
    print("-----------------------------------------")
    time.sleep(2)

  except Exception as e:
    print(e)

commitDataToFile()