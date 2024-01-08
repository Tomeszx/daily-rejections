from selenium.webdriver.chrome.webdriver import WebDriver
from daily_rejection.page_objects.base_methods import BaseMethods, Locator
from result import Ok, Err, Result


class UnmergeTab(BaseMethods):
    unmerge_tab_button = Locator(arg='//button[@id="unmerge-tab"]')
    content = Locator(arg='//div[@id="unmerge" and @class="tab-pane fade active show"]')
    pms_url = Locator(arg='//*[@id="unmergeTableBody"]/tr/td[2]/a')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def go_to_unmerge_tab(self) -> None:
        self.wait_for_clickability(self.unmerge_tab_button).click()
        self.wait_for_visibility(self.content)

    def _get_all_urls(self, shop_name: str) -> list:
        pms_links = []
        for elem in self.get_elements(self.pms_url):
            shop_name_cell = " ".join(elem.get_attribute("textContent").split(" ")[1:-1])

            if shop_name.split('(')[0].lower() == shop_name_cell.split('(')[0].lower():
                pms_links.append(elem.get_attribute("href"))
        return pms_links

    def find_pms_url(self, shop_name: str) -> Result[list, list]:
        if pms_urls := self._get_all_urls(shop_name):
            return Ok(pms_urls)
        return Err(["AK", "OOS", "NO", "", "", "pms link not found"])
