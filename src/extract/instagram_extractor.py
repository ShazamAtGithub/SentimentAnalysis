import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

website = '' # Site url
class InstagramCommentsExtractor:
    def __init__(self, exporter_url=website, headless=True, download_dir=None):
        self.exporter_url = exporter_url
        self.driver = None
        self.wait = None

        # Setup download directory
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_dir, exist_ok=True)

        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")

        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_settings.popups": 0,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        # Anti bot detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            print("WebDriver initialized.")
        except WebDriverException as e:
            print(f"Error initializing WebDriver: {e}")

    def extract_comments(self, instagram_post_url):
        if not self.driver:
            print("WebDriver not initialized.")
            return None

        try:
            self.driver.get(self.exporter_url)
            print("Loaded Export Comments website")
            time.sleep(3)

            # Input the Instagram post url
            url_input = self.wait.until(EC.presence_of_element_located((By.ID, "export_url")))
            url_input.clear()
            url_input.send_keys(instagram_post_url)
            print("Entered Instagram post url")

            # Primary and alternate selectors
            try:
                export_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(@class, 'btn-lg')]")))
            except TimeoutException:
                export_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Export') or contains(@class, 'export')]")))

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_button)
            time.sleep(2)

            # JavaScript click
            self.driver.execute_script("arguments[0].click();", export_button)
            print("Started export process")
            time.sleep(10)

            # Download button selectors
            try:
                download_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and .//i[contains(@class, 'download')]]")))
            except TimeoutException:
                download_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@title, 'Download') or contains(@class, 'download')]")))

            self.driver.execute_script("arguments[0].click();", download_button)
            time.sleep(2)

            # Export button selectors
            try:
                excel_option = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Save as Excel File')]")
                ))
            except TimeoutException:
                try:
                    excel_option = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(text(), 'Excel') or contains(@title, 'Excel')]")
                    ))
                except TimeoutException:
                    excel_option = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(@class, 'excel') or contains(@class, 'xls')]")
                    ))

            self.driver.execute_script("arguments[0].click();", excel_option)
            print("Selected Excel download option")
            return self._wait_for_download()

        except Exception as e:
            print(f"Extraction error: {e}")

        return None

    def _wait_for_download(self):
        print("Waiting for download to complete...")
        start_time = time.time()
        timeout = 60

        # Get list of files pre-download
        files_before = set(os.listdir(self.download_dir))
        while time.time() - start_time < timeout:
            # Filter out new files
            current_files = set(os.listdir(self.download_dir))
            new_files = current_files - files_before
            temp_files = [f for f in new_files if
                          f.endswith('.part') or f.endswith('.crdownload') or f.endswith('.tmp')]
            if temp_files:
                time.sleep(2)
                continue
            # Check for new complete Excel files
            excel_files = [f for f in new_files if f.endswith('.xlsx')]
            if excel_files:
                latest_file = max([os.path.join(self.download_dir, f) for f in excel_files],
                                  key=os.path.getctime)
                file_size = os.path.getsize(latest_file)
                time.sleep(2)
                if file_size == os.path.getsize(latest_file):
                    # Validate the file
                    try:
                        pd.read_excel(latest_file)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_file = os.path.join(self.download_dir, f"instagram_comments_{timestamp}.xlsx")
                        # Rename file
                        os.rename(latest_file, new_file)
                        print(f"Downloaded and renamed to: {new_file}")
                        return new_file
                    except Exception as e:
                        print(f"Downloaded file is invalid: {e}")
            time.sleep(1)
        print("Download timeout.")
        return None

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed.")



