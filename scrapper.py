from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrapper_helper import *

# Your login credentials
username = 'Service@energieversum.de'
password = 'Ey8iNk4s13'
login_url = 'https://mein-senec.de/auth/login'
main_page_url = 'https://mein-senec.de/installateur/#!customers'
fileName = 'senec_scrapped.xlsx'

chromedriver_path = 'D:/Training/Scrapper/chromedriver.exe'
driver = webdriver.Chrome(executable_path=chromedriver_path)

# Main part of the script
login(driver, username, password, login_url)
waitForLoading(driver)
data = iterateOverTable(driver, main_page_url)
commitDataToFile(fileName, data)