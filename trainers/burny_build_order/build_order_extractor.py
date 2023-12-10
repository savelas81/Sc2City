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

from sc2city.utils import OrderType
from sc2city.game_objects import Order
from config import BurnyOrder, TYPES, EXCEPTION_IDS


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
                "id": order["name"].upper(),
                "type": order_type,
                "can_skip": can_skip,
                "priority": priority,
                "target_value": 1,
                "comment": "Write comment here",
            }
            for order, priority, (order_type, can_skip) in zip(
                build_order, priorities, order_types
            )
        ]
        return formatted_orders

    def __get_type(self, order: BurnyOrder) -> tuple[str, bool]:
        new_type = (
            EXCEPTION_IDS[order["name"]]
            if order["name"] in EXCEPTION_IDS
            else TYPES[order["type"]]
        )
        can_skip = False if new_type == OrderType.STRUCTURE.name else True
        return new_type, can_skip

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
