import json
import re

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from daily_rejection.page_objects.base_methods import BaseMethods, Locator
from result import Ok, Err, Result

ONE_SIZE_NAMES = ["onesize", "tu", "os", "taglita", "nvt", "uni", "stk", "unica", "tagliaunica", "n"]
with open("../Projekt Ani/daily_rejection/sizes_map/child_sizes.json") as file:
    CHILD_SIZES = json.loads(file.read())


class SizesAndPricesTab(BaseMethods):
    size_tab = Locator(arg='//*[@id="tab-sizes"]/span')
    size_tab_active = Locator(arg='//div[@id="tab-sizes" and @class="el-tabs__item is-top is-active"]')
    cell_sizes = Locator(arg='//tr/td[2]')
    cell_stock = Locator(arg='../td[4]')
    cells_in_row = Locator(arg='../td')
    prices = Locator(arg='./span[@class="line-through-value"]')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def go_to_size_tab(self) -> None | list:
        self.wait_for_clickability(self.size_tab).click()
        try:
            self.wait_for_presence(self.size_tab_active)
        except Exception:
            return ["AK", "Dupa blada w PM", "Nie otwiera się size tab", "", "", ""]

    def _get_all_sizes(self) -> dict[str, WebElement]:
        pattern = r"[^a-z0-9]|eu|fr|it|cm|us"
        return {
            re.sub(pattern, "", elem.get_attribute("textContent").lower()): elem
            for elem in self.get_elements(self.cell_sizes)
        }

    @staticmethod
    def _check_additional_conditions_for_size(expected_size: str, sizes_pm: dict) -> bool:
        if (size := CHILD_SIZES.get(expected_size)) in sizes_pm:
            return Ok(sizes_pm[size])
        elif (size := json.loads('../daily_rejection/sizes_map/pm_exceptions_1.json').get(expected_size)) in sizes_pm:
            return Ok(sizes_pm[size])
        elif (size := json.loads('../daily_rejection/sizes_map/pm_exceptions__2.json').get(expected_size)) in sizes_pm:
            return Ok(sizes_pm[size])
        elif size := [one_size for one_size in ONE_SIZE_NAMES if one_size in sizes_pm]:
            return Ok(sizes_pm[size[0]])
        return Err(["AK", "Undefined", "Undefined", "Sizes in PM ->", " | ".join(sizes_pm), ""])


    def find_product_size(self, expected_size: str, expected_prod_size: str) -> Result[WebElement, list]:
        sizes_pm = self._get_all_sizes()
        if not sizes_pm:
            return Err(["AK", "Stock not updated on time", "YES", "", "", ""])

        if expected_size in sizes_pm:
            return Ok(sizes_pm[expected_size])
        elif (size := re.sub(r"[^a-z0-9]|eu|fr|it|cm|us", "", expected_prod_size)) in sizes_pm:
            return Ok(sizes_pm[size])

        return self._check_additional_conditions_for_size(expected_size, sizes_pm)

    def check_product_stock(self, element: WebElement) -> Result[None, list]:
        if int(element.find_element(*self.cell_stock).text) < 1:
            return Err(["AK", "Stock not updated on time", "YES", "", "Stock not updated on time", ""])
        return Ok(None)

    def _get_prices(self, element: WebElement) -> list:
        return [
            (
                price_elem.text
                for price_elem in cell_elem.find_elements(self.prices)
            )
            for cell_elem in element.find_elements(*self.cells_in_row)[4:]
        ]

    @staticmethod
    def _check_price_range(given_price: str, expected_price: float) -> bool:
        return 97 < (float(given_price) / expected_price) * 100 < 103

    def check_product_price(self, element: WebElement, expected_price: float) -> Result[list, list]:
        for price_cell in self._get_prices(element):
            if self._check_price_range(price_cell[0], expected_price):
                return Ok(["AK", "Standard Rejection", "NO", self.driver.current_url, "", f'Given: {price_cell[0]}'])
            elif "n/a" not in price_cell and self._check_price_range(price_cell[1], expected_price):
                return Ok(["AK", "Standard Rejection", "NO", self.driver.current_url, "", f'Given: {price_cell[1]}'])
        return Ok(["AK", "Price mis-match", "NO", "", "Price has changed", ""])
