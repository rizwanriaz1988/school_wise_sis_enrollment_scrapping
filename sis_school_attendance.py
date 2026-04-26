from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
# Initialize driver
chrome = webdriver.Chrome()
chrome.set_page_load_timeout(60)

# Open the webpage
chrome.get("https://sis.pesrp.edu.pk/")

try:
    # 1. Wait and click the attendance tab
    attendance_tab = WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "attendance-tab")))
    attendance_tab.click()

    # 2. Wait for the first dropdown (district) to be present
    district = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="attendance_tab_form"]/div[1]/select')))
    
    # Scroll the element into view
    chrome.execute_script("arguments[0].scrollIntoView(true);", district)
    
    # Wait until the dropdown is interactable
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable(district))
    
    # Select district value
    district_select = Select(district)
    district_select.select_by_value('33')
    time.sleep(3)
    # 3. Wait for tehsil dropdown to be present
    tehsil = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="attendance_tab_form"]/div[2]/select')))
    
    # Scroll and wait for interactivity
    chrome.execute_script("arguments[0].scrollIntoView(true);", tehsil)
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable(tehsil))
    
    # Select tehsil value
    tehsil_select = Select(tehsil)
    tehsil_select.select_by_value('116')
    time.sleep(3)
    # 4. Wait for markaz dropdown to be present
    markaz = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="attendance_tab_form"]/div[3]/select')))
    
    # Scroll and wait for interactivity
    chrome.execute_script("arguments[0].scrollIntoView(true);", markaz)
    WebDriverWait(chrome, 20).until(EC.element_to_be_clickable(markaz))
    
    # Select markaz value
    markaz_select = Select(markaz)
    # markaz_select.select_by_value('6450')  # 6450 for markaz bhikhi
    markaz_select.select_by_value('6469')  # 6450 for markaz sadar
    time.sleep(3)
    print("Successfully selected all dropdown options.")

    # school_value=[31925,32015,32017,32033,32034,32035,32044,32045,32049,32441] # schools value list for markaz bhikhi
    school_value=[32001] # schools value list for markaz sadar

    for value in school_value:
        # Wait for school dropdown to be present
        school = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="attendance_tab_form"]/div[4]/select')))
        
        # Scroll and wait for interactivity
        chrome.execute_script("arguments[0].scrollIntoView(true);", school)
        WebDriverWait(chrome, 20).until(EC.element_to_be_clickable(school))
        
        # Select school value
        school_select = Select(school) 
        school_select.select_by_value(str(value))
        time.sleep(3)

        # 5. Click the filter button
        filter_button = WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div/div/div/div/div[3]/div[3]/div[2]/div[1]/div/form/div[7]/button')))
        filter_button.click()
        time.sleep(5)
        print("Filter button clicked.")

        # 6. Wait for the chart to be present   (//*[name()='svg'])[5]//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']
        parent_element_path = "((//*[name()='svg'])[5]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[2]"
        chart = WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))
        print("Chart found.")

        # Find all rect elements within the parent element
        path_elements = chart.find_elements(By.TAG_NAME, "path")
        print("Path elements found:",len(path_elements))
        print("Type of path elements",type(path_elements))
        # parent_element_path = "((//*[name()='svg'])[1]//*[name()='g' and @class='highcharts-series-group']//*[name()='g'])[1]"
        # parent_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, parent_element_path)))
        # time.sleep(5)

        # # Find all rect elements within the parent element
        # rect_elements = parent_element.find_elements(By.TAG_NAME, "rect")
        # print(len(rect_elements))
        # time.sleep(2)

        # # Initialize ActionChains for hover action
        actions = ActionChains(chrome)
        time.sleep(2)
        # Scraping the chart data
        # for path[-1] in path_elements:
        attendance_status = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][4]"
        present_std = "//*[name()='svg']//*[name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-undefined']//*[name()='text']//*[name()='tspan'][3]"

        for path in path_elements:
            print("Path element", path)

            # Hover over the element
            actions.move_to_element(path).perform()
            time.sleep(2)  # Let tooltip render fully

            try:
                # Use visibility (not just presence) — tooltip must be visible
                school_attendance_status = WebDriverWait(chrome, 10).until(
                    EC.visibility_of_element_located((By.XPATH, attendance_status))
                )
                school_present_std = WebDriverWait(chrome, 10).until(
                    EC.visibility_of_element_located((By.XPATH, present_std))
                )

                # Re-hover AGAIN right before grabbing text (tooltip can vanish during wait)
                actions.move_to_element(path).perform()
                time.sleep(0.5)

                school_attendance = school_attendance_status.text
                school_present = school_present_std.text

                print(f"Attendance Status: {school_attendance}, Present Students: {school_present}")

            except Exception as e:
                print(f"Could not extract tooltip for path element: {e}")
                continue

            time.sleep(1)



        # 7. Hover over the chart





except TimeoutException as e:
    print(f"Timeout occurred: {str(e)}")
except ElementNotInteractableException as e:
    print(f"Element not interactable: {str(e)}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # Optional: Close the browser when done (uncomment if you want the browser to close at the end)
    # chrome.quit()
    pass  # Keep the browser open for debugging