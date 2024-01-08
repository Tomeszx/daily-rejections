from selenium.webdriver.chrome.webdriver import WebDriver
from daily_rejection.page_objects.base_methods import BaseMethods, Locator
from result import Ok, Err, Result


class StockTab(BaseMethods):
    stock_tab_button = Locator(arg='//button[@id="stock-tab"]')
    content = Locator(arg='//div[@id="itemTabContent"]')
    location_cell = Locator(arg='//*[@id="stock"]/table/tbody/tr/td[2]')
    stock_cell = Locator(arg='../td[3]')
    shop_name_cell = Locator(arg='../td[2]')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def go_to_stock_tab(self, details_tab_url: str) -> None:
        self.open(details_tab_url)
        self.wait_for_clickability(self.stock_tab_button).click()
        self.wait_for_visibility(self.content)

    def check_details(self, shop_name: str) -> Result[None, list]:
        for elem in self.get_elements(self.location_cell):
            shop_name_cell = " ".join(elem.get_attribute("textContent").split(" ")[1:-1])

            if shop_name.split('(')[0].lower() == shop_name_cell.split('(')[0].lower():
                if int(elem.find_element(*self.stock_cell).get_attribute("textContent")) > 0:
                    return Ok(None)
        return Err(["AK", "OOS", "NO", "", "", "details stock not passed"])

