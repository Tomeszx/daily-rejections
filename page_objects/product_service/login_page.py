from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from daily_rejection.page_objects.base_methods import BaseMethods, Locator


class LoginPage(BaseMethods):
    username_input = Locator(By.ID, "username")
    password_input = Locator(By.ID, "password")
    submit_button = Locator(arg='//*[@type="submit"]')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def login(self, username: str, password: str) -> None:
        self.open('https://proxy-product.miinto.net/auth/login')
        self.wait_for_clickability(self.username_input)

        self.write(self.username_input, username)
        self.write(self.password_input, password)
        self.click(self.submit_button)
        self.wait_for(only_readystate=True)
