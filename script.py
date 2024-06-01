import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

# Path to ChromeDriver
chrome_driver_path = '/path/to/chromedriver'  # Update this path if needed

# Create a webdriver instance using undetected_chromedriver
driver = uc.Chrome(driver_executable_path=chrome_driver_path, headless=True)

# List of websites to visit
websites = [
    'https://example.com',
    'https://anotherexample.com'
]

# Target link text to search for
target_link_text = 'Desired Link Text'

for website in websites:
    driver.get(website)
    try:
        # Wait for the element to be present
        link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, target_link_text)))
        print(f'Found link at {website}: {link.get_attribute("href")}'
    except Exception as e:
        print(f'Link not found at {website}: {str(e)}')

# Close the browser
driver.quit()


