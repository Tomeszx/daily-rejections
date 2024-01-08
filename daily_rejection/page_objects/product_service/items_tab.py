import json
import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from daily_rejection.page_objects.base_methods import BaseMethods, Locator
from result import Ok, Err, Result


with open("../Projekt Ani/daily_rejection/sizes_map/child_sizes.json") as file:
    CHILD_SIZES = json.loads(file.read())


class ItemsTab(BaseMethods):
    items_tab_button = Locator(arg='//button[@id="items-tab"]')
    cell_sizes = Locator(arg='//div[@class="updateItemText"]')
    prod_size = Locator(arg='../..//td[4]/div')
    cell_details_link = Locator(arg='../..//a[@class="btn btn-outline-primary"]')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def go_to_items_tab(self) -> Result[None, list]:
        try:
            self.wait_for_clickability(self.items_tab_button, 15).click()
            self.wait_for_clickability(self.items_tab_button, 15)
        except TimeoutException:
            return Err(["AK", "PC product not found", "YES", "", "", ""])
        return Ok[None]

    def _get_all_sizes_from_page(self) -> dict:
        sizes_pc = {}
        for elem in self.get_elements(self.cell_sizes):
            text_elem = elem.get_attribute("textContent").lower().split("_")[-1]
            sizes_pc[re.sub(r"[^a-z0-9]", "", text_elem)] = elem
        return sizes_pc

    def _get_mathing_row_data(self, element: WebElement) -> dict:
        return {
            'url': element.find_element(*self.cell_details_link).get_attribute("href"),
            'prod_size': element.find_element(*self.prod_size).get_attribute("textContent")
        }

    def find_size(self, size: str) -> Result[dict, list]:
        sizes_pc = self._get_all_sizes_from_page()

        if not sizes_pc:
            msg = "Incorrectly processed data (wrong merge, size mapped incorrectly etc)"
            return Err(["AK", msg, "YES", "", "", ""])
        elif size in sizes_pc:
            return Ok(self._get_mathing_row_data(sizes_pc[size]))
        elif (child_size := CHILD_SIZES.get(size)) in sizes_pc:
            return Ok(self._get_mathing_row_data(sizes_pc[child_size]))
        elif any("y" in size for size in sizes_pc):
            return Err(["AK", "Y size in PC", "", "ROZMIARY W PC ->", " | ".join(sizes_pc), ""])
        return Err(["AK", "OOS", "NO", "ROZMIARY W PC ->", " | ".join(sizes_pc), ""])

