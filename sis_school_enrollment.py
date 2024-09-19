# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service  # Correct way to specify ChromeDriver path
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from selenium.webdriver import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd
# from datetime import datetime

# # for google integrations
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# import os

# # Path to your ChromeDriver
# chrome_driver_path = '/usr/bin/chromedriver'
# # Use Service to specify ChromeDriver path
# service = Service(executable_path=chrome_driver_path)

# # Optional: Set Chrome options if needed
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")

# # Initialize WebDriver with Service and Options
# chrome = webdriver.Chrome(service=service, options=chrome_options)

# # Open the website
# url = 'https://sis.punjab.gov.pk/'
# chrome.get(url)

# # Navigate to the 'students_search' tab
# WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.ID, "students_search-tab"))).click()

# # Select district and tehsil
# district = Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[1]/select'))))
# district.select_by_value('33')  # Replace with actual district value

# # Select tehsil
# tehsil = Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[2]/select'))))
# tehsil.select_by_value('116')  # Replace with actual tehsil value

# # Select markaz (markaz ids range from 6449 to 6469)
# markaz= Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[3]/select'))))

# # Prepare to scrape data
# marakaz_list = []

# # for loop for looping through marakaz
# # for markaz_id in range(6449, 6470):
# for markaz_id in range(6449, 6450):

#     markaz.select_by_value(str(markaz_id))
#     time.sleep(5)

#     # Click on the filter/search button
#     filter_button_xpath = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[12]/div[3]/div/div/div/div[1]/div/form/div[7]/button'
#     WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, filter_button_xpath))).click()

  

#     time.sleep(5)
#     # Locate the parent element by XPath
#     parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
#     parent_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))
#     time.sleep(5)
#     # Find all rect elements within the parent element
#     rect_elements = parent_element.find_elements(By.TAG_NAME, "rect")
#     print(len(rect_elements))
#     time.sleep(2)
#     # # Initialize ActionChains for hover action
#     actions = ActionChains(chrome)
#     time.sleep(2)
#     # Scraping the chart data
#     for i, bar in enumerate(rect_elements):
#         time.sleep(2)
#         # Perform hover action on each rect element
#         actions.move_to_element(bar).perform()

#         # Pause to ensure the tooltip appears
#         time.sleep(2)
        

#        # Define the XPaths for the elements
#         school_emis_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][1]"
#         school_total_enroll_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][3]"

#         try:
#             # Use WebDriverWait to wait until elements are present
#             school_emis_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, school_emis_xpath)))
#             school_total_enroll_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, school_total_enroll_xpath)))

#             # Extract the text from the elements
#             school_emis = school_emis_element.text
#             school_total_enroll = school_total_enroll_element.text

#             # Process the text
#             school_enroll = school_total_enroll[7:]  # Adjust this slicing based on your data format

#             # Update the marakaz dictionary
#             marakaz_list.append({
#                 'EMIS Code': school_emis,
#                 'Enrollment': school_enroll
#             })

#         except Exception as e:
#             print(f"An error occurred: {e}")

#         # print(marakaz_list)
#         print(len(marakaz_list))


# # Convert the list of dictionaries to a DataFrame

# df = pd.DataFrame(marakaz_list)

# # Get the current date and time
# current_date = datetime.now().strftime("%d-%m-%Y")  # Format: YYYY-MM-DD

# # Save the DataFrame to an Excel file
# excel_filename = f"school_wise_enrollment_data_{current_date}.xlsx"
# df.to_excel(excel_filename, index=False, engine='openpyxl')

# print(f"Data saved to {excel_filename}")


# # ===============================GOOGLE INTEGRATION==============================================
# # ===============================GOOGLE INTEGRATION==============================================

# SERVICE_ACCOUNT_FILE = '/home/runner/service_account_credentials.json'  # Path in GitHub Actions
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# sheets_service = build('sheets', 'v4', credentials=credentials)

# # The ID of your Google Sheets spreadsheet and the range to update
# SPREADSHEET_ID = '1i0KG-we9EqZt-PeAPxYscKpVb60sfpq-OcVISJz3a7g'  # Replace with your spreadsheet ID
# RANGE_NAME = 'Sheet1!A1'  # Replace with your desired range

# # Load data from Excel file
# df = pd.read_excel(excel_filename)

# # Convert DataFrame to a list of lists
# data = df.values.tolist()
# header = df.columns.tolist()

# # Prepare the data to be uploaded
# values = [header] + data

# # Call the Sheets API
# body = {
#     'values': values
# }

# result = sheets_service.spreadsheets().values().update(
#     spreadsheetId=SPREADSHEET_ID,
#     range=RANGE_NAME,
#     valueInputOption='RAW',
#     body=body
# ).execute()

# print(f"{result.get('updatedCells')} cells updated in Google Sheets.")

import time
import base64
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Path to the Base64-encoded Google credentials from the environment variable
BASE64_ENCODED_GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEET_CREDENTIALS')


if BASE64_ENCODED_GOOGLE_CREDENTIALS is None or BASE64_ENCODED_GOOGLE_CREDENTIALS == '':
    raise ValueError("The environment variable GOOGLE_SHEET_CREDENTIALS is not set or is empty.")


# Decode and save the Base64-encoded Google credentials
credentials_file_path = '/home/runner/service_account_credentials.json'
with open(credentials_file_path, 'wb') as f:
    f.write(base64.b64decode(BASE64_ENCODED_GOOGLE_CREDENTIALS))

# Path to your ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'
service = Service(executable_path=chrome_driver_path)

# Optional: Set Chrome options if needed
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Initialize WebDriver with Service and Options
chrome = webdriver.Chrome(service=service, options=chrome_options)

# Open the website
url = 'https://sis.punjab.gov.pk/'
chrome.get(url)

# Navigate to the 'students_search' tab
WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.ID, "students_search-tab"))).click()

# Select district and tehsil
district = Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[1]/select'))))
district.select_by_value('33')  # Replace with actual district value

tehsil = Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[2]/select'))))
tehsil.select_by_value('116')  # Replace with actual tehsil value

markaz = Select(WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[3]/select'))))


# Prepare to scrape data
marakaz_list = []

for markaz_id in range(6449, 6450):
    markaz.select_by_value(str(markaz_id))
    time.sleep(5)

    # Click on the filter/search button
    filter_button_xpath = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[12]/div[3]/div/div/div/div[1]/div/form/div[7]/button'
    WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, filter_button_xpath))).click()

    time.sleep(5)
    parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
    parent_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))
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
            school_emis_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, school_emis_xpath)))
            school_total_enroll_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, school_total_enroll_xpath)))

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
current_date = datetime.now().strftime("%d-%m-%Y")  # Format: YYYY-MM-DD

# Save the DataFrame to an Excel file
excel_filename = f"school_wise_enrollment_data_{current_date}.xlsx"
df.to_excel(excel_filename, index=False, engine='openpyxl')

print(f"Data saved to {excel_filename}")

# ===============================GOOGLE INTEGRATION==============================================
SERVICE_ACCOUNT_FILE = '/home/runner/service_account_credentials.json'  # Path in GitHub Actions
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

# The ID of your Google Sheets spreadsheet and the range to update
SPREADSHEET_ID = '1i0KG-we9EqZt-PeAPxYscKpVb60sfpq-OcVISJz3a7g'  # Replace with your spreadsheet ID
RANGE_NAME = 'Sheet1!A1'  # Replace with your desired range

# Load data from Excel file
df = pd.read_excel(excel_filename)

# Convert DataFrame to a list of lists
data = df.values.tolist()
header = df.columns.tolist()

# Prepare the data to be uploaded
values = [header] + data

# Call the Sheets API
body = {
    'values': values
}

result = sheets_service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME,
    valueInputOption='RAW',
    body=body
).execute()

print(f"{result.get('updatedCells')} cells updated in Google Sheets.")


