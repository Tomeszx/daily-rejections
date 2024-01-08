from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver

from daily_rejection.page_objects.base_methods import BaseMethods, Locator
from result import Ok, Err, Result


class ProductInformationTab(BaseMethods):
    details_tab_button = Locator(arg='//button[@id="items-tab"]')
    error_404 = Locator(arg='//*[@id="miinto-interface"]/section/main/div/h1')
    product_status = Locator(arg='//div[@class="el-alert__content"]/span')
    deactivate_button = Locator(arg='//div[@role="switch" and @aria-checked="true"]')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def go_to_details_page(self) -> Result[None, list]:
        try:
            self.wait_for_clickability(self.details_tab_button).click()
        except TimeoutException as e:
            if error_elem := self.get_elements(self.error_404):
                if "404Not Found" in error_elem[0].text:
                    msg = "Product deleted from the feed"
                    return Err(["AK", msg, "YES", "", "", "PRODUCT UNMERGED DUE TO SYNC ERROR"])
                raise NotImplementedError("-") from e
        self.wait_for_clickability(self.details_tab_button)
        return Ok(None)

    def check_product_status(self) -> Result[None, list]:
        if len(status := self.get_elements(self.product_status)) < 2:
            return Err(["AK", "Stock not updated on time", "YES", "", "", ""])
        elif "Product status:valid" not in status[0].text and "Product status:processed" not in status[1].text:
            return Err(["AK", "Stock not updated on time", "YES", "", "", ""])
        return Ok(None)

    def deactivate_product(self) -> bool:
        if deactivate_button := self.get_elements(self.deactivate_button):
            self.driver.execute_script("arguments[0].click();", deactivate_button[0])
            return True
        return False

