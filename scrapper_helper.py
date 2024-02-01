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

def onlyPushHighLevelInfo(row, dataValues):
    # print("Locked Row Content: ", row.find_element_by_xpath(".//td[2]").text)
    dataValues.append({
                    'Installation': '--',
                    'Installationsdatum': '--',
                    'Name': row.find_element_by_xpath(".//td[2]").text,
                    'Firma': '--',
                    'Ort': '--',
                    'E-Mail': '--',
                    'Straße': '--',
                    'Telefon': '--',
                    'Anzahl Module': '--',
                    'Kapazität': '--'
                })
    return dataValues

def clickRow(driver, rowCount, rows):
    current_row = rows[rowCount]
    first_column = current_row.find_element_by_xpath(".//td[1]")
    if "v-table-cell-content-meinsenec-padlock-wrench" not in first_column.get_attribute("class"):
        print("Clicking the Row", rowCount + 1)
        ActionChains(driver).move_to_element(current_row).perform()
        current_row.click()
        return True
    else:
        print("Skipping the row with paddle lock")
        return False

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

def scrapeDataForCustomer(driver, data_list):
    installations = getTableValues(driver, 'Installation')
    besitzer = getTableValues(driver, 'Name')
    akku = getTableValues(driver, 'Technologie')
    return appendValues(data_list, installations, besitzer, akku)

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

def scrollToBottom(driver):
    print("Trying to scroll to Bottom")
    # Send the down arrow key multiple times to simulate scrolling down
    for _ in range(10):  # Adjust the number of times you want to press the key
        ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
        # time.sleep(1)  # Adjust the delay as needed
    time.sleep(5)
    print("Done scrolling to Bottom")

def inputSearch(driver):
    number_input = driver.find_element(By.CLASS_NAME, "meinsenec-searchfield")
    number_input.clear()  # Clear any existing text
    number_input.send_keys("986353504")  # Enter your desired number
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    print("Data Searched")
    wait(5)

def iterateOverTable(driver, target_url):
    wait(5)
    row = 0
    data_list = []
    retires = 3;
    while True:
        try:
            goToKunden(driver, target_url)
            
            # Wait for the table to be present
            table = loadTable(driver)
            # inputSearch(driver)
            # table = loadTable(driver)
            rows = table.find_elements_by_tag_name('tr')

            if row >= len(rows):
                header_element = driver.find_element_by_css_selector(".v-table-caption-container.v-table-caption-container-align-center")
                header_element.click()
                ActionChains(driver).move_to_element(rows[len(rows) - 1]).perform()
                scrollToBottom(driver)
                rows = table.find_elements_by_tag_name('tr')
                print("Rows Loaded: ", len(rows))

            print("Kunden Page Loaded Found Rows in the table: ", len(rows))

            if row < len(rows):
                retires = 0

                isClicked = clickRow(driver, row, rows)
                if isClicked:
                    print("Opening Page after click")
                    waitForDataPageToLoad(driver)
                    data_list = scrapeDataForCustomer(driver, data_list)
                else:
                    print("Row not clicked scrapping high level info")
                    data_list = onlyPushHighLevelInfo(rows[row], data_list)
                row += 1
                print("On row: ", row)
                # row = int(input("Enter row number you want to jump to : "))
                
            else:
                print("No more rows - Scrolling More")
                scrollToBottom(driver)
                retires -= 1
                if retires == 0:
                    break

        except TimeoutException as e:
            print(f"Error: {e}")
            print("Timeout: Table not found within the specified time. Exiting.")
            retires -= 1
            if retires == 0:
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