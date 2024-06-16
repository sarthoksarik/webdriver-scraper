from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime

class WebScraperHeadless:
    def __init__(self, target_url):
        self.target_url = target_url
        self.setup_logging()
        self.driver = self.setup_driver()

    def setup_logging(self):
        logging.basicConfig(filename='results_headless.log', level=logging.INFO, format='%(message)s')

    def setup_driver(self):
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Set the user-agent string to match a typical browser
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')

        # Disable the webdriver flags or make it appear as not automated
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Further disguise the headless driver by adding capabilities
        options.add_argument('--disable-blink-features')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Initialize the driver
        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        driver.set_page_load_timeout(15)
        return driver

    def accept_cookies(self):
        try:
            cookie_button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
            )
            cookie_button.click()
        except (TimeoutException, NoSuchElementException):
            pass

    def find_urls(self, url):
        try:
            self.driver.get(url)
            self.accept_cookies()
            links = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
            )
            found = False
            all_nofollow = True
            for link in links:
                href = link.get_attribute('href')
                if self.target_url in href:
                    found = True
                    rel = link.get_attribute('rel')
                    if rel is None or 'nofollow' not in rel:
                        all_nofollow = False
                        break

            if found:
                return (datetime.now().strftime('%Y/%m/%d'), not all_nofollow, all_nofollow)
            else:
                return ('not found', None, None)
        except Exception as e:
            logging.error(f"An error occurred while processing {url}: {str(e)}")
            return ('error', None, None)

    def close_driver(self):
        self.driver.quit()


