from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Set up proxy settings
proxy = "http://52.67.10.183:80"

chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--headless')  # Run in headless mode for CI/CD
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')

# Initialize WebDriver with proxy settings
chrome_driver_path = '/usr/bin/chromedriver'
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the webpage
driver.get("https://sis.punjab.gov.pk/")

# Take screenshot
screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
driver.save_screenshot(screenshot_filename)

# Close the browser
driver.quit()

print(f"Screenshot saved as {screenshot_filename}")
