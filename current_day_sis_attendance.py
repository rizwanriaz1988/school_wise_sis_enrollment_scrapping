"""
Teachers Attendance Monitor - Markaz Bhikhi
-------------------------------------------
Scrapes Punjab SIS attendance for Markaz Bhikhi schools.
Generates a report of schools with 0 attendance in both:
1. Local folder: teachers_attendance_report.txt
2. WSL workspace: WSL_WORKSPACE_DIR/teachers_attendance_report.txt

Features:
- Skips certain weekdays (e.g., Friday, Saturday, Sunday)
- Skips ad-hoc dates listed in dates.txt
- Reports skipped days with date in DD-MM-YYYY format
- Can run headless or normal via configuration
"""

# 1️⃣ Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
from datetime import datetime
from pathlib import Path

# 2️⃣ Configuration
URL = "https://sis.pesrp.edu.pk/"
DISTRICT_VALUE = '33'
TEHSIL_VALUE = '116'
ATTENDANCE_TAB_ID = "attendance-tab"
FILTER_BUTTON_XPATH = '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[3]/div[2]/div[1]/div/form/div[7]/button'
ATTENDANCE_TSPAN_XPATH = """
((//*[name()='svg'])[4]
 //*[name()='g' and contains(@class,'highcharts-data-labels')
 and contains(@class,'highcharts-series-0')
 and contains(@class,'highcharts-pie-series')]
 //*[name()='g'])[1]
 //*[name()='text']//*[name()='tspan'][3]
"""

# MARKAZ_SCHOOLS updated for Markaz Bhikhi
MARKAZ_SCHOOLS = {
    '6450': [31925,32015,32017,32033,32034,32035,32044,32045,32049,32441],  # Markaz Bhikhi
}

# Attendance deadline
ATTENDANCE_DEADLINE = "16:00"  # 24-hour format

# Rerun interval (10 minutes)
RERUN_INTERVAL = 10 * 60

# WSL workspace directory
WSL_WORKSPACE_DIR = Path(r"\\wsl.localhost\Ubuntu\home\rizwan\.openclaw\workspace\dengue_report")
WSL_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

# Report files
WSL_REPORT_FILE = WSL_WORKSPACE_DIR / "teachers_attendance_report.txt"
LOCAL_REPORT_FILE = Path("teachers_attendance_report.txt")  # local folder

# Days of week to skip
SKIP_WEEKDAYS = ["Friday", "Saturday", "Sunday"]

# Dates file to skip (DD-MM-YYYY format per line)
DATES_FILE = WSL_WORKSPACE_DIR / "dates.txt"

# Headless configuration: True = headless, False = normal
HEADLESS_MODE = True

# 3️⃣ Helper Functions
def select_dropdown(driver, xpath, value):
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(element))
    select = Select(element)
    select.select_by_value(str(value))
    time.sleep(2)
    selected_text = select.first_selected_option.text.strip()
    school_name = " ".join(selected_text.split()[1:])  # skip EMIS code
    return school_name

def click_filter(driver):
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, FILTER_BUTTON_XPATH))
    )
    button.click()
    print("Filter button clicked.")
    time.sleep(5)

def extract_chart_value(driver):
    def get_value(driver):
        try:
            element = driver.find_element(By.XPATH, ATTENDANCE_TSPAN_XPATH)
            return driver.execute_script("return arguments[0].textContent.trim();", element)
        except:
            return False
    value = WebDriverWait(driver, 30).until(get_value)
    return value

def generate_report(pending_schools, skipped=False):
    now = datetime.now()
    timestamp = now.strftime("%I:%M%p, %d-%m-%Y")
    lines = ["TEACHERS SIS ATTENDANCE", timestamp, "\nAttendance Pending:"]
    if skipped:
        lines.append("Attendance check skipped today (weekend or holiday).")
    else:
        for school in pending_schools:
            lines.append(f" {school}")

    # Write to WSL workspace
    with open(WSL_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Write to local folder
    with open(LOCAL_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Report saved. Pending schools count: {len(pending_schools) if not skipped else 0}")

def is_deadline_passed():
    now = datetime.now()
    deadline_time = datetime.strptime(ATTENDANCE_DEADLINE, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    return now >= deadline_time

def is_skip_day():
    """
    Returns True if today is in SKIP_WEEKDAYS or listed in dates.txt
    """
    today = datetime.now()
    weekday = today.strftime("%A")
    today_str = today.strftime("%d-%m-%Y")
    
    # Skip if weekday matches
    if weekday in SKIP_WEEKDAYS:
        return True

    # Skip if today is in dates.txt
    if DATES_FILE.exists():
        with open(DATES_FILE, "r", encoding="utf-8") as f:
            skip_dates = [line.strip() for line in f.readlines()]
            if today_str in skip_dates:
                return True

    return False

# 4️⃣ Main Monitoring Logic
def monitor_attendance():
    if is_skip_day():
        print("Today is a skipped day. Generating skipped report.")
        generate_report([], skipped=True)
        return

    # Configure Chrome options
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    chrome = webdriver.Chrome(options=options)
    chrome.set_page_load_timeout(60)
    chrome.get(URL)

    try:
        attendance_tab = WebDriverWait(chrome, 20).until(
            EC.element_to_be_clickable((By.ID, ATTENDANCE_TAB_ID))
        )
        attendance_tab.click()
        select_dropdown(chrome, '//*[@id="attendance_tab_form"]/div[1]/select', DISTRICT_VALUE)
        select_dropdown(chrome, '//*[@id="attendance_tab_form"]/div[2]/select', TEHSIL_VALUE)

        while True:
            if is_deadline_passed():
                print("Attendance deadline passed. Exiting monitor.")
                break

            pending_schools = []

            for markaz_id, schools in MARKAZ_SCHOOLS.items():
                select_dropdown(chrome, '//*[@id="attendance_tab_form"]/div[3]/select', markaz_id)

                for school_id in schools:
                    school_name = select_dropdown(chrome, '//*[@id="attendance_tab_form"]/div[4]/select', school_id)
                    click_filter(chrome)
                    attendance_value = extract_chart_value(chrome)
                    print(f"Markaz: {markaz_id}, School: {school_name}, Attendance: {attendance_value}")

                    if attendance_value == "0":
                        pending_schools.append(school_name)

            generate_report(pending_schools)

            if not pending_schools:
                print("No pending schools. All attendance marked.")
                break

            print(f"Pending schools exist. Re-running after {RERUN_INTERVAL//60} minutes...")
            time.sleep(RERUN_INTERVAL)

    except TimeoutException as e:
        print(f"Timeout occurred: {str(e)}")
    except ElementNotInteractableException as e:
        print(f"Element not interactable: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        chrome.quit()

# Run monitor
if __name__ == "__main__":
    monitor_attendance()