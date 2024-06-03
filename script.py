from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to ChromeDriver
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

# Iterate over each website
for website in websites:
    # Open the website
    driver.get(website)

    # Locate all <a> tag elements
    link_elements = driver.find_elements_by_tag_name('a')

    # Initialize a boolean to track if a match is found
    found = False

    # Iterate over each element and check the href attribute
    for link_element in link_elements:
        link_href = link_element.get_attribute('href')
        if link_href == desired_url:
            found = True
            break

    # Print result
    if found:
        print(f'yes ({website})')
    else:
        print(f'no ({website})')

# Close the browser
driver.quit()



