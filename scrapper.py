import json
from selenium import webdriver
from scrapper_helper import *

# Load configuration from config.json
with open('scrapper-configs.json') as config_file:
    config = json.load(config_file)

# Extract variables from config
username = config.get('username')
password = config.get('password')
login_url = config.get('login_url')
main_page_url = config.get('main_page_url')
fileName = config.get('fileName')
chromedriver_path = config.get('chromedriver_path')

# Initialize webdriver
driver = webdriver.Chrome(executable_path=chromedriver_path)

# Main part of the script
login(driver, username, password, login_url)
waitForLoading(driver)
data = iterateOverTable(driver, main_page_url)
commitDataToFile(fileName, data)
