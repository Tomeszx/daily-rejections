import os
import re
import threading

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService

from daily_rejection import interface
from daily_rejection.google_sheet import open_google_sheets
from daily_rejection.page_objects.product_management_service.login_page import LoginPage as PmsLoginPage
from daily_rejection.page_objects.product_service.login_page import LoginPage as PsLoginPage
from daily_rejection.page_objects.product_management_service.product_information_tab import ProductInformationTab
from daily_rejection.page_objects.product_management_service.sizes_and_prices_tab import SizesAndPricesTab
from daily_rejection.page_objects.product_service.items_tab import ItemsTab
from daily_rejection.page_objects.product_service.unmerge_tab import UnmergeTab
from daily_rejection.page_objects.product_service.stock_tab import StockTab
from gspread_dataframe import set_with_dataframe
from result import is_err, Result, Ok

os.environ["WDM_LOG_LEVEL"] = "0"


def check_product_management_service(driver: WebDriver, gs_data: dict, ps_data: tuple) -> Result:
    pm_information_tab = ProductInformationTab(driver)
    pm_sizes_and_prices_tab = SizesAndPricesTab(driver)
    err_responses = []

    for pm_link in list(set(ps_data[1])):
        driver.get(pm_link)
        
        pm_information_tab.go_to_details_page()
        response = pm_information_tab.check_product_status()
        if is_err(response):
            err_responses.append(response)
            continue
        
        matching_row_response = pm_sizes_and_prices_tab.find_product_size(gs_data['size'], ps_data[0]['prod_size'])
        if is_err(matching_row_response):
            err_responses.append(matching_row_response)
            continue

        final_response = pm_sizes_and_prices_tab.check_product_stock(matching_row_response.ok_value)
        if is_err(final_response):
            err_responses.append(final_response)
            continue

        result = pm_sizes_and_prices_tab.check_product_price(matching_row_response.ok_value, gs_data['price'])
        if result.ok_value[1] == "Standard Rejection":
            print(f'Deactivated: {pm_information_tab.deactivate_product()}')
        return result
    return err_responses[-1]


def check_product_service(driver: WebDriver, gs_data: dict) -> Result[tuple[dict, list], list]:
    driver.get(gs_data['url'])
    
    ps_items_tab = ItemsTab(driver)
    login_result = ps_items_tab.go_to_items_tab()
    if is_err(login_result):
        return login_result
    data_response = ps_items_tab.find_size(gs_data['size'])
    if is_err(data_response):
        return data_response

    ps_unmerge_tab = UnmergeTab(driver)
    ps_unmerge_tab.go_to_unmerge_tab()
    pm_urls = ps_unmerge_tab.find_pms_url(gs_data['shop_name'])
    if is_err(pm_urls):
        return pm_urls
    
    ps_stock_tab = StockTab(driver)
    ps_stock_tab.go_to_stock_tab(data_response.ok_value['url'])
    result = ps_stock_tab.check_details(gs_data['shop_name'])
    if is_err(result):
        return result
    return Ok((data_response.ok_value, pm_urls.ok_value))


def map_values(row: list) -> dict:
    return {
        'shop_name': row[14],
        'size': re.sub(r"[^a-z0-9]", "", row[10].lower()),
        'location': row[13],
        'order_id': row[0],
        'url': row[12],
        'price': round(float(row[23]), 2)
    }


def process_all_rows(driver: WebDriver, start_index: int, end_index: int, data: list[list]) -> None:
    df = pd.DataFrame(columns=[
        'MiintoCheckedBy', 'MiintoDeclineReason', 'Miinto fee exclude', 'Link to PM ', 'Miinto Comment', 'Action'
    ])

    for i, row in enumerate(data[start_index:end_index]):
        gs_data = map_values(row)
        print(f"\n\n >>>>>>>>> {gs_data}")

        if not row[0]:
            df.loc[start_index+i+1] = ["", "", "", "", "", ""]
            continue
        
        ps_result = check_product_service(driver, gs_data)
        if is_err(ps_result):
            df.loc[start_index + i + 1] = ps_result.err_value
            continue
            
        pms_result = check_product_management_service(driver, gs_data, ps_result.ok_value)
        if is_err(pms_result):
            df.loc[start_index + i + 1] = pms_result.err_value

    x = open_google_sheets()[0]
    set_with_dataframe(x, df, include_column_header=False, row=start_index + 1, col=43)


def login_to_all_services(driver: WebDriver, user_args) -> None:
    PsLoginPage(driver).login(user_args.username_ps, user_args.password_ps)
    PmsLoginPage(driver).login(user_args.username_pms, user_args.password_pms)


def get_webdriver() -> WebDriver:
    chromedriver_options = webdriver.ChromeOptions()
    chromedriver_options.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )
    chromedriver_options.add_argument("--disable-extensions")
    chromedriver_options.add_argument("--headless")
    chromedriver_options.add_argument("--window-size=1920,1080")
    chromedriver_options.add_argument("--disable-gpu")
    chromedriver_options.page_load_strategy = "eager"
    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": os.getcwd()
    }
    chromedriver_options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=chromedriver_options, service=ChromeService())


def run_with_threads(user_args) -> None:
    google_sheet, all_data = open_google_sheets()

    threads = []
    l = 1
    for _ in range(user_args.threads_num):
        start_index = l
        l += int(len(all_data) / user_args.threads_num)
        end_index = min(l, len(all_data))

        driver = get_webdriver()
        login_to_all_services(driver, user_args)
        current_thread = threading.Thread(target=process_all_rows, args=(driver, start_index, end_index, all_data))

        threads.append(current_thread)
        current_thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    user_args = interface.handle()
    run_with_threads(user_args)
