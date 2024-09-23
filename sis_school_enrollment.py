import random
import time
import base64
import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# List of user-agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
]

# Decode Base64-encoded Google Sheets credentials from environment variable
BASE64_ENCODED_GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEET_CREDENTIALS')
if BASE64_ENCODED_GOOGLE_CREDENTIALS is None:
    raise ValueError("The environment variable GOOGLE_SHEET_CREDENTIALS is not set or is empty.")

SERVICE_ACCOUNT_FILE = '/home/runner/service_account_credentials.json'
with open(SERVICE_ACCOUNT_FILE, 'wb') as f:
    f.write(base64.b64decode(BASE64_ENCODED_GOOGLE_CREDENTIALS))

chrome_driver_path = '/usr/bin/chromedriver'
service = Service(executable_path=chrome_driver_path)

# Set up Chrome options with a random user-agent
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument('--proxy-server=http://8.219.97.248:80')  # Use your proxy if required

# Disable extensions and enable remote debugging for troubleshooting
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--remote-debugging-port=9222")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Initialize the Chrome driver
chrome = webdriver.Chrome(service=service, options=chrome_options)
chrome.set_page_load_timeout(30)

# The website URL to scrape
url = 'https://sis.punjab.gov.pk/'

# Maximum retry attempts for loading the page
max_retries = 3

try:
    for attempt in range(max_retries):
        try:
            chrome.get(url)
            print("Page loaded successfully.")
            logging.info("Page loaded successfully")

            # Capture screenshot after page load
            screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            chrome.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

            break
        except TimeoutException as e:
            print(f"Attempt {attempt + 1} failed due to timeout. Retrying in 5 seconds...")
            logging.error(f"Error loading page: {e}")
            time.sleep(5)
        except WebDriverException as e:
            print(f"WebDriver exception encountered: {e}")
            raise
    
    # Continue with the scraping and other tasks...
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "students_search-tab"))).click()

    district = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[1]/select'))))
    district.select_by_value('33')  # Choose a specific district by value

    tehsil = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[2]/select'))))
    tehsil.select_by_value('116')  # Choose a specific tehsil by value

    markaz = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[3]/select'))))

    marakaz_list = []

    for markaz_id in range(6449, 6470):  # Adjust the range based on available Markaz IDs
        markaz.select_by_value(str(markaz_id))
        time.sleep(random.uniform(3, 7))  # Random wait between 3 to 7 seconds

        filter_button_xpath = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[12]/div[3]/div/div/div/div[1]/div/form/div[7]/button'
        WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.XPATH, filter_button_xpath))).click()

        time.sleep(random.uniform(3, 7))  # Random wait after clicking the filter

        parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
        parent_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))

        rect_elements = parent_element.find_elements(By.TAG_NAME, "rect")
        print(len(rect_elements))

        actions = ActionChains(chrome)

        for bar in rect_elements:
            actions.move_to_element(bar).perform()
            time.sleep(random.uniform(1, 3))  # Random wait for tooltip to appear

            school_emis_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][1]"
            school_total_enroll_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][3]"

            try:
                school_emis_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_emis_xpath)))
                school_total_enroll_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_total_enroll_xpath)))

                school_emis = school_emis_element.text
                school_total_enroll = school_total_enroll_element.text
                school_enroll = school_total_enroll[7:]

                marakaz_list.append({
                    'EMIS Code': school_emis,
                    'Enrollment': school_enroll
                })

            except Exception as e:
                print(f"An error occurred: {e}")
                raise

        print(len(marakaz_list))

    # Save scraped data to Excel
    df = pd.DataFrame(marakaz_list)
    current_date = datetime.now().strftime("%d-%m-%Y")
    excel_filename = f"school_wise_enrollment_data_{current_date}.xlsx"
    df.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"Data saved to {excel_filename}")

    # Google Sheets API integration
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=credentials)

    SPREADSHEET_ID = '1i0KG-we9EqZt-PeAPxYscKpVb60sfpq-OcVISJz3a7g'
    RANGE_NAME = 'Sheet1!A1'

    # Load the Excel file into a dataframe and upload to Google Sheets
    df = pd.read_excel(excel_filename)
    df.fillna('', inplace=True)
    data = df.values.tolist()
    header = df.columns.tolist()
    values = [header] + data

    body = {
        'values': values
    }

    # Clear existing data in Google Sheet before uploading
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()

    print(f"{result.get('updatedCells')} cells updated in Google Sheets.")

except Exception as e:
    print(f"An error occurred during the scraping process: {e}")
    logging.error(f"Scraping failed: {e}")
finally:
    chrome.quit()
