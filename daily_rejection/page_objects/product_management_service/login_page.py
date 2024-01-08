from selenium.webdriver.chrome.webdriver import WebDriver

from daily_rejection.page_objects.base_methods import BaseMethods, Locator


class LoginPage(BaseMethods):
    username_input = Locator(arg='//*[@id="miinto-interface"]/section/main/div/div/form/div[1]/div/div/input')
    password_input = Locator(arg='//*[@id="miinto-interface"]/section/main/div/div/form/div[2]/div/div/input')
    submit_button = Locator(arg='//*[@id="miinto-interface"]/section/main/div/div/form/div[3]/div/button')

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def login(self, username: str, password: str) -> None:
        self.open('https://proxy-pms.miinto.net/auth/login')
        self.wait_for_clickability(self.username_input)

        self.write(self.username_input, username)
        self.write(self.password_input, password)
        self.click(self.submit_button)
        self.wait_for(only_readystate=True)
