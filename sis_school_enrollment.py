import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Decode Base64-encoded credentials
BASE64_ENCODED_GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEET_CREDENTIALS')
if BASE64_ENCODED_GOOGLE_CREDENTIALS is None:
    raise ValueError("The environment variable GOOGLE_SHEET_CREDENTIALS is not set or is empty.")

# Decode and save credentials to a file
SERVICE_ACCOUNT_FILE = '/home/runner/service_account_credentials.json'
with open(SERVICE_ACCOUNT_FILE, 'wb') as f:
    f.write(base64.b64decode(BASE64_ENCODED_GOOGLE_CREDENTIALS))

# Set up ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'
service = Service(executable_path=chrome_driver_path)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

chrome = webdriver.Chrome(service=service, options=chrome_options)

# Set a longer page load timeout
chrome.set_page_load_timeout(60)  # Timeout set to 60 seconds

# Retry mechanism
url = 'https://sis.punjab.gov.pk/'
max_retries = 3  # Number of retries

for attempt in range(max_retries):
    try:
        chrome.get(url)
        print("Page loaded successfully.")
        break
    except TimeoutException:
        print(f"Attempt {attempt + 1} failed. Retrying in 5 seconds...")
        time.sleep(5)
else:
    raise Exception("Failed to load the page after several attempts.")

# Navigate to the 'students_search' tab
WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "students_search-tab"))).click()

# Select district and tehsil
district = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[1]/select'))))
district.select_by_value('33')  # Replace with actual district value

tehsil = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[2]/select'))))
tehsil.select_by_value('116')  # Replace with actual tehsil value

markaz = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[3]/select'))))

# Prepare to scrape data
marakaz_list = []

# Loop through markaz IDs
# for markaz_id in range(6449, 6450):
for markaz_id in range(6449, 6470):
    markaz.select_by_value(str(markaz_id))
    time.sleep(5)

    # Click on the filter/search button
    filter_button_xpath = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[12]/div[3]/div/div/div/div[1]/div/form/div[7]/button'
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.XPATH, filter_button_xpath))).click()

    time.sleep(5)
    parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
    parent_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))
    time.sleep(5)
    rect_elements = parent_element.find_elements(By.TAG_NAME, "rect")
    print(len(rect_elements))
    time.sleep(2)
    actions = ActionChains(chrome)
    time.sleep(2)

    for i, bar in enumerate(rect_elements):
        time.sleep(2)
        actions.move_to_element(bar).perform()
        time.sleep(2)

        school_emis_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][1]"
        school_total_enroll_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][3]"

        try:
            school_emis_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_emis_xpath)))
            school_total_enroll_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_total_enroll_xpath)))

            school_emis = school_emis_element.text
            school_total_enroll = school_total_enroll_element.text

            school_enroll = school_total_enroll[7:]  # Adjust this slicing based on your data format

            marakaz_list.append({
                'EMIS Code': school_emis,
                'Enrollment': school_enroll
            })

        except Exception as e:
            print(f"An error occurred: {e}")

        print(len(marakaz_list))

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(marakaz_list)

# Get the current date and time
current_date = datetime.now().strftime("%d-%m-%Y")

# Save the DataFrame to an Excel file
excel_filename = f"school_wise_enrollment_data_{current_date}.xlsx"
df.to_excel(excel_filename, index=False, engine='openpyxl')

print(f"Data saved to {excel_filename}")

# Google Sheets Integration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

SPREADSHEET_ID = '1i0KG-we9EqZt-PeAPxYscKpVb60sfpq-OcVISJz3a7g'  # Replace with your spreadsheet ID
RANGE_NAME = 'Sheet1!A1'

df = pd.read_excel(excel_filename)
df.fillna('', inplace=True)  # Replace NaN with empty string
data = df.values.tolist()
header = df.columns.tolist()
values = [header] + data

body = {
    'values': values
}

# Clear the existing data in the range
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


