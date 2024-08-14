
import time
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RERADataScraper:
    def __init__(self, driver_path):
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")

        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        self.data_list = []

    def load_page(self, url):
        try:
            self.driver.get(url)
            print("Page loaded successfully.")
        except Exception as e:
            print("An error occurred while loading the page:")
            print(e)
            traceback.print_exc()

    def click_listing(self, index):
        try:
            if index == 0:
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(20)

            listings = self.driver.find_elements(By.XPATH, "//div[@class='col-lg-6']//div[@class='shadow py-3 px-3 font-sm radius-3 mb-2']/div/a")
            if index < len(listings):
                listing = listings[index]
                listing.click()
                print(f"Clicked on listing {index + 1}.")
                return True
            else:
                print(f"Listing {index + 1} not found.")
                return False
        except Exception as e:
            print(f"An error occurred while clicking on listing {index + 1}:")
            print(e)
            traceback.print_exc()
            return False

    def extract_data(self):

        data_dict = {}
        try:
            data_dict["RERA No"] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Ref. No. ')]/./span"))
            ).text

            data_dict["Name"] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Name')]/../td[2]"))
            ).text

            data_dict["GST No"] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'GSTIN No.')]/../td[2]/span"))
            ).text

            data_dict["PAN No"] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'PAN No.')]/../td[2]/span"))
            ).text

            data_dict["Permanent Address"] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Permanent Address')]/../td[2]/span"))
            ).text

            print(f"Data collected: {data_dict}")
            return data_dict

        except Exception as e:
            print("An error occurred while extracting data:")
            print(e)
            traceback.print_exc()
            return None

    def go_back(self):
        try:
            back_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-header']/button")))
            back_button.click()
            print("Back to Home page")
            time.sleep(10)
        except Exception as e:
            print("Error clicking the back button:")
            print(e)
            traceback.print_exc()

    def scrape_data(self, url, max_listings=10):
        self.load_page(url)

        for i in range(max_listings):
            if self.click_listing(i):
                data = self.extract_data()
                if data:
                    self.data_list.append(data)
                self.go_back()
            else:
                break

    def save_to_excel(self, filename):
        try:
            df = pd.DataFrame(self.data_list)
            df.to_excel(filename, index=False)
            print(f"Data saved to '{filename}'.")
        except Exception as e:
            print("An error occurred while saving the data to Excel:")
            print(e)
            traceback.print_exc()

    def quit(self):

        self.driver.quit()

if __name__ == "__main__":
    try:
        scraper = RERADataScraper('chromedriver.exe')
        scraper.scrape_data("https://hprera.nic.in/PublicDashboard")
        scraper.save_to_excel("scraped_data.xlsx")
    except Exception as e:
        print("An error occurred during the scraping process:")
        print(e)
        traceback.print_exc()
    finally:
        scraper.quit()