from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support import expected_conditions as EC

chrome_driver_path = 'chromedriver'  # Update this path if needed

# Set up Chrome options
chrome_options = Options()
# Do not use headless mode
# chrome_options.add_argument('--headless')

# Optionally add other arguments to make the browser look more like a user is using it
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# List of websites to check
websites = [
    'https://imgur.com/gallery/artisan-adolf-M0PAnba',
    'https://my.weezevent.com/decouverte-du-metier-de-charpentier',
    'https://fr.foursquare.com/v/artisan-adolf-r%C3%A9novation/65000fb67ade9f58be1182fd'
]

# Define the URL to match
desired_url = 'https://artisan-adolf-renovation.fr'
desired_url = 'https://artisan-adolf-renovation.fr'
# Iterate over each website


# Define the URL to match

# Iterate over each website
for website in websites:
    # Wait for the page to fully load and other scripts to execute
# Wait for the page to fully load and other scripts to execute
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    
    found = False
    nofollow = False

    driver.get(website)
    link_elements = driver.find_elements(By.TAG_NAME, 'a')
    for link_element in link_elements:
            found = True
            nofollow = False
            # Check for nofollow attribute
            if 'nofollow' in link_element.get_attribute('rel'):
                nofollow = True
            else:
                break
        tag_names = ['link', 'meta', 'script', 'img']
        for tag in tag_names:
            elements = driver.find_elements(By.TAG_NAME, tag)
            for element in elements:
                # Handle different attributes based on tag types
                url = None
                if tag in ['link', 'img']:
                    url = element.get_attribute('href')
                elif tag == 'meta':
                    url = element.get_attribute('content')
                elif tag == 'script':
                    script_content = element.get_attribute('innerHTML')
                    try:
                        data = json.loads(script_content)
                        if 'url' in data:
                            url = data['url']
                    except json.JSONDecodeError:
                        pass
                
                if url == desired_url:
                    found = True
                    nofollow = False
                    # Check for nofollow attribute
                    if 'nofollow' in element.get_attribute('rel'):
                        nofollow = True
                    else:
                        break
if found:
    if nofollow:
        print(f'Found a nofollow link to {desired_url} in {website}')
    else:
        print(f'Found a dofollow link to {desired_url} in {website}')
else:
    print(f'No link to {desired_url} found in {website}')


                
# Close the browser
driver.quit()









