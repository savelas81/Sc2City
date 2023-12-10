import os
import time
import json
import uuid
import pyperclip

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BuildOrderExtractor:
    download_folder = "build_orders"
    timeout = 15

    def __init__(self, url: str, download_dir: str):
        self.url = url
        self.download_dir = os.path.join(download_dir, self.download_folder)

    def get_build_order(self) -> None:
        self.__copy_build_order()
        # Wait for the clipboard content to be available
        time.sleep(1)  # adjust this delay as needed
        clipboard_content = pyperclip.paste()
        self.__save_build_order(clipboard_content)

    def __save_build_order(self, build_order: str) -> None:
        filename = str(uuid.uuid4()) + ".json"
        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, "w") as f:
            build_order_obj = json.loads(build_order)
            self.__format_build_order(build_order_obj)
            json.dump(build_order_obj, f, indent=2)

    def __format_build_order(self, build_order: dict) -> None:
        current_priority = len(build_order) * 5
        for order in build_order:
            current_priority -= 5
            order["id"] = order["name"]
            order["priority"] = current_priority
            order["target_value"] = 1
            order["comment"] = "Write comment here"
            del order["name"]
            del order["supply"]
            del order["time"]
            del order["frame"]

    def __copy_build_order(self) -> None:
        driver = self.__get_driver()
        wait = WebDriverWait(driver, self.timeout)
        driver.get(self.url)
        action = ActionChains(driver)

        hover_menu = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="root"]/div/div/div/div[1]/div[2]/div[1]/div[3]',
                )
            )
        )
        action.move_to_element(hover_menu).perform()
        copy_button = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="root"]/div/div/div/div[1]/div[2]/div[1]/div[3]/div/div[3]/div',
                )
            )
        )
        copy_button.click()

    def __get_driver(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
            },
        )
        driver = webdriver.Chrome(options=chrome_options)
        return driver


import os

dir_path = os.path.dirname(os.path.realpath(__file__))

url = "https://burnysc2.github.io/sc2-planner/?&race=terran&bo=002eJy9UssKwjAQ/Jc992Cy1tT+ingobZAgtCUmiIj/7q0R7I5tkF4zzOw8cnqS66jelwWFx2ippvvgr9bTq/iFqOOE3IKPbYjeLqDpHaBBkCesaYMb+iXHtqEoFAmBOb0DJC0SexfSUqyBB7yjIKkNIBmpQtyFcCqnCUb2IAjbYFhVJbSfXMbx4pvuQ4/nKVwhhwdRT7IgWkN5xBXXXpFSrtXJSlGqeZL0/q9w21S7Np0y33/n/AYyNOO0"
bo_extractor = BuildOrderExtractor(url, dir_path)
bo_extractor.get_build_order()
