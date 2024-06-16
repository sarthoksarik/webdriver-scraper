from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime

class WebScraper:
    def __init__(self, target_url):
        self.target_url = target_url
        self.setup_logging()
        self.driver = self.setup_driver()

    def setup_logging(self):
        logging.basicConfig(filename='results.log', level=logging.INFO, format='%(message)s')

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
                    # print("found")
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
