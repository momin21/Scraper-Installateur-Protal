from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd

def wait(waitingTime):
    time.sleep(waitingTime)

def login(driver, username, password, login_url):
    print("Login")
    # Step 1: Perform the login
    driver.get(login_url)
    # Wait for a while to ensure the page is fully loaded
    time.sleep(1)
    # Find the username and password fields and enter your credentials
    username_field = driver.find_element_by_name("username")
    password_field = driver.find_element_by_name("password")
    username_field.send_keys(username)
    password_field.send_keys(password)
    # Submit the form
    password_field.send_keys(Keys.RETURN)
    print("Login Done")
    # Wait for a while to ensure the login is complete
    return

def waitForLoading(driver):
    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'v-app-loading')))
    print("Installateur Loaded")
    return

def goToKunden(driver, target_url):
    driver.get(target_url)
    return

def appendValues(dataValues, installations, besitzer, akku):
    dataValues.append({
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
    return dataValues

def commitDataToFile(fileName, data):
    # data needs to be saved to file
    try:
        print("Committing Data to " + fileName )
        df = pd.DataFrame(data)
        df.to_excel(fileName, index=False)
        print("Data pushed successfully")
    except Exception as e:
        print("Data not pushed successfully", e)
    return

def loadTable(driver):
    return WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-table-table')))

def waitForDataPageToLoad(driver):
     WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'v-tabsheet-tabsheetpanel')))
     print("Data Loaded")
     return

def clickRow(driver, rowCount, rows):
    print("Clicking the Row", rowCount + 1)
    ActionChains(driver).move_to_element(rows[rowCount]).perform()
    rows[rowCount].click()
    return

def getTableValues(driver, tableName):
    print("trying to parse ", tableName)
    installation_table = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//table[.//span[text()="'+ tableName +'"]]')))
    print("Table"+ tableName +" Found")
    values_dict = {}
    dataRows = installation_table.find_elements(By.TAG_NAME, 'tr')
        # Loop through each row and extract values
    # Print the extracted values
    for row in dataRows:
        caption = row.find_element(By.CLASS_NAME, 'v-formlayout-captioncell').find_element(By.TAG_NAME, 'span').text.strip()
        value = row.find_element(By.CLASS_NAME, 'v-formlayout-contentcell').find_element(By.TAG_NAME, 'div').text.strip()
        values_dict[caption] = value
    return values_dict

def iterateOverTable(driver, target_url):
    wait(5)
    row = 0
    data_list=[]
    while True:
        try:
            goToKunden(driver, target_url)
            
            # Wait for the table to be present
            table = loadTable(driver)
            rows = table.find_elements_by_tag_name('tr')
            print("Kunden Page Loaded Found Rows in the table: ", len(rows))

            if row < len(rows):
                clickRow(driver, row, rows)
                waitForDataPageToLoad(driver)
				
                installations = getTableValues(driver, 'Installation')                
                besitzer = getTableValues(driver, 'Name')
                akku = getTableValues(driver, 'Technologie')
                
                data_list = appendValues(data_list, installations, besitzer, akku)
                # input("Input if you want to skip to a specific number of row: ")
                row += 1
                
            else:
                print("No more rows - Exiting")
                break
                
        except TimeoutException as e:
            print(f"Error: {e}")
            print("Timeout: Table not found within the specified time. Exiting.")
            break
        except NoSuchElementException as e:
            print(f"Error: {e}")
            print("Element not found. Exiting.")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("An unexpected error occurred. Exiting.")
            break
    # print("Rows scrapped: ", len(data_list))
    return data_list