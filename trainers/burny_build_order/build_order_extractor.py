import os
import time
import json
import uuid
import pyperclip

import concurrent.futures
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from sc2city.utils import OrderType
from sc2city.game_objects import Order
from config import BurnyOrder, TYPES, EXCEPTION_IDS, BURNY_ACTIONS


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
            formatted_orders = self.__format_build_order(build_order_obj)
            json.dump(formatted_orders, f, indent=2)

    def __format_build_order(self, build_order: list[BurnyOrder]) -> list[Order]:
        priorities = range(len(build_order) * 5, 0, -5)
        order_types = map(self.__get_type, build_order)

        formatted_orders = [
            {
                "id": new_id,
                "type": order_type,
                "can_skip": can_skip,
                "priority": priority,
                "quantity": 1,
                "comment": "Write comment here",
            }
            for priority, (new_id, order_type, can_skip) in zip(priorities, order_types)
        ]
        return formatted_orders

    def __get_type(self, order: BurnyOrder) -> tuple[str, str, bool]:
        new_id = (
            BURNY_ACTIONS[order["name"]]
            if order["name"] in BURNY_ACTIONS
            else order["name"].upper()
        )
        new_type = (
            EXCEPTION_IDS[order["name"]]
            if order["name"] in EXCEPTION_IDS
            else TYPES[order["type"]]
        )
        can_skip = False if new_type == OrderType.STRUCTURE.name else True
        return new_id, new_type, can_skip

    def __copy_build_order(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.__get_chrome_driver)
            try:
                driver = future.result(
                    timeout=self.timeout
                )  # Set timeout to 10 seconds
            except concurrent.futures.TimeoutError:
                driver = self.__get_firefox_driver()
            except Exception as e:
                print(f"An error occurred: {e}")

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

    def __get_chrome_driver(self) -> webdriver.Chrome:
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
            },
        )
        return webdriver.Chrome(options=chrome_options)

    def __get_firefox_driver(self) -> webdriver.Firefox:
        firefox_options = FirefoxOptions()
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference(
            "browser.download.manager.showWhenStarting", False
        )
        firefox_options.set_preference("browser.download.dir", self.download_dir)
        firefox_options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/pdf"
        )
        firefox_options.set_preference(
            "pdfjs.disabled", True
        )  # disable the built-in PDF viewer
        return webdriver.Firefox(options=firefox_options)
