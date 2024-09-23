import time
import base64
import sys  # Import sys for exit functionality
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

# Decode Base64-encoded Google Sheets credentials from environment variable
BASE64_ENCODED_GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEET_CREDENTIALS')
if BASE64_ENCODED_GOOGLE_CREDENTIALS is None:
    raise ValueError("The environment variable GOOGLE_SHEET_CREDENTIALS is not set or is empty.")

# Decode the credentials and save them as a JSON file for Google Sheets API access
SERVICE_ACCOUNT_FILE = '/home/runner/service_account_credentials.json'
with open(SERVICE_ACCOUNT_FILE, 'wb') as f:
    f.write(base64.b64decode(BASE64_ENCODED_GOOGLE_CREDENTIALS))

# Set up ChromeDriver with appropriate options
chrome_driver_path = '/usr/bin/chromedriver'  # Path to ChromeDriver executable
service = Service(executable_path=chrome_driver_path)

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")  # Set user agent

# Initialize the Chrome WebDriver with specified options
chrome = webdriver.Chrome(service=service, options=chrome_options)
chrome.set_page_load_timeout(30)  # Set maximum page load time to 30 seconds

# Define the URL to scrape
url = 'https://sis.punjab.gov.pk/'
max_retries = 3  # Maximum number of retries for loading the page

try:
    # Attempt to load the specified URL with retries
    for attempt in range(max_retries):
        try:
            chrome.get(url)  # Load the webpage
            print("Page loaded successfully.")  # Log success message
            break  # Exit retry loop if successful
        except TimeoutException as e:
            print(f"Attempt {attempt + 1} failed due to timeout. Retrying in 5 seconds...")
            print(f"Exception: {e}")  # Log timeout exception
            time.sleep(5)  # Wait before retrying to load the page
        except WebDriverException as e:
            print(f"WebDriver exception encountered: {e}")  # Log any WebDriver-related issues
            raise  # Re-raise exception to fail the build
    else:
        raise Exception("Failed to load the page after several attempts.")  # Raise an error if the page failed to load after all attempts

    # Wait for the 'students_search' tab to be clickable and click it
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "students_search-tab"))).click()

    # Select district and tehsil from dropdown menus
    district = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[1]/select'))))
    district.select_by_value('33')  # Replace with actual district value (value can vary)

    tehsil = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[2]/select'))))
    tehsil.select_by_value('116')  # Replace with actual tehsil value (value can vary)

    # Prepare to select 'markaz' from another dropdown
    markaz = Select(WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="enrollment_tab_form"]/div[3]/select'))))

    # List to store scraped data
    marakaz_list = []

    # Loop through specified markaz IDs to scrape enrollment data
    for markaz_id in range(6449, 6470):  # Adjust the range of markaz IDs as needed
        markaz.select_by_value(str(markaz_id))  # Select the current markaz by ID
        time.sleep(5)  # Wait for the data to load (consider replacing with WebDriverWait)

        # Click the filter/search button to submit the selected values
        filter_button_xpath = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[12]/div[3]/div/div/div/div[1]/div/form/div[7]/button'
        WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.XPATH, filter_button_xpath))).click()

        time.sleep(5)  # Wait for results to load after clicking the filter button
        parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
        parent_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))

        # Find all rectangle elements that represent the data bars in the chart
        rect_elements = parent_element.find_elements(By.TAG_NAME, "rect")
        print(len(rect_elements))  # Log the number of data bars found

        actions = ActionChains(chrome)  # Initialize action chains for mouse movements

        # Loop through each rectangle (data bar) to extract enrollment data
        for bar in rect_elements:
            actions.move_to_element(bar).perform()  # Hover over the bar to trigger the tooltip
            time.sleep(2)  # Wait for the tooltip to appear

            # XPaths for extracting EMIS code and total enrollment from the tooltip
            school_emis_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][1]"
            school_total_enroll_xpath = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][3]"

            try:
                # Wait for the tooltip elements to be present and extract their text
                school_emis_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_emis_xpath)))
                school_total_enroll_element = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, school_total_enroll_xpath)))

                school_emis = school_emis_element.text  # Extract EMIS code
                school_total_enroll = school_total_enroll_element.text  # Extract total enrollment
                school_enroll = school_total_enroll[7:]  # Adjust this slicing based on the format of the total enrollment data

                # Append the scraped data to the list
                marakaz_list.append({
                    'EMIS Code': school_emis,
                    'Enrollment': school_enroll
                })

            except Exception as e:
                print(f"An error occurred: {e}")  # Log any exceptions that occur during data extraction
                raise  # Re-raise exception to fail the build

        print(len(marakaz_list))  # Log the current count of collected data

    # Convert the list of dictionaries into a pandas DataFrame for easy manipulation
    df = pd.DataFrame(marakaz_list)

    # Get the current date and format it for the filename
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Save the DataFrame to an Excel file
    excel_filename = f"school_wise_enrollment_data_{current_date}.xlsx"
    df.to_excel(excel_filename, index=False, engine='openpyxl')  # Save as Excel without the index column
    print(f"Data saved to {excel_filename}")  # Log the filename where data was saved

    # Setup Google Sheets API integration
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=credentials)  # Build the Sheets API service

    SPREADSHEET_ID = '1i0KG-we9EqZt-PeAPxYscKpVb60sfpq-OcVISJz3a7g'  # Replace with your actual spreadsheet ID
    RANGE_NAME = 'Sheet1!A1'  # Specify the range to update in Google Sheets

    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_filename)
    df.fillna('', inplace=True)  # Replace NaN values with empty strings for cleaner data
    data = df.values.tolist()  # Convert DataFrame values to a list
    header = df.columns.tolist()  # Get the column headers
    values = [header] + data  # Combine header and data for Google Sheets

    body = {
        'values': values  # Create the request body for Google Sheets API
    }

    # Clear existing data in the specified range before updating
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    # Update the Google Sheets with the new data
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',  # Use raw values to avoid formatting issues
        body=body
    ).execute()

    print(f"{result.get('updatedCells')} cells updated in Google Sheets.")  # Log the number of cells updated

except Exception as e:
    print(f"An error occurred: {e}")  # Log any errors that occur during execution
    sys.exit(1)  # Exit the script with a non-zero exit code to indicate failure

finally:
    chrome.quit()  # Ensure the Chrome browser is closed after scraping is complete
