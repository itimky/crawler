import pickle
from os import path

from antigate import AntiGate
from htmlmin.decorator import htmlmin
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

from .config import HUB_URL, KEY_ANTIGATE


class DriverContextManager(object):
    def __init__(self, make_driver):
        self.make_driver = make_driver
        self.driver = None

    def __enter__(self):
        if not self.driver:
            self.driver = self.make_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # self.driver.get("about:blank")
            self.driver.delete_all_cookies()
            # self.driver.execute_script('localStorage.clear();')
        except WebDriverException:
            pass
        return False


def context_manager(fn):
    def wrapper():
        if not wrapper.dcm:
            wrapper.dcm = DriverContextManager(fn)
        return wrapper.dcm
    wrapper.dcm = None
    return wrapper


@context_manager
def get_chrome_ipv4():
    capabilities = DesiredCapabilities.CHROME
    capabilities['applicationName'] = 'chrome-ipv4'
    driver = webdriver.Remote(
        command_executor=HUB_URL,
        desired_capabilities=capabilities)
    return driver


@context_manager
def get_chrome_ipv6():
    capabilities = DesiredCapabilities.CHROME
    capabilities['applicationName'] = 'chrome-ipv6'
    driver = webdriver.Remote(
        command_executor=HUB_URL,
        desired_capabilities=capabilities)
    return driver


@htmlmin
def get_soup(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    for s in soup(['script', 'style']):
        s.decompose()
    return str(soup)


def load_cookies(driver, file):
    try:
        with open(path.join('/tmp', file), 'rb') as f:
            for cookie in pickle.load(f):
                driver.add_cookie(cookie)
    except FileNotFoundError:
        pass


def save_cookies(driver, file):
    with open(path.join('/tmp', file), 'wb') as f:
        pickle.dump(driver.get_cookies(), f)


def solve_captcha(img_filename, is_russian=True):
    gate_config = {'is_russian': int(is_russian)}
    cap_text = AntiGate(KEY_ANTIGATE, img_filename,
                        send_config=gate_config)
    return cap_text.get()


def wait_for_jquery_ajax(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return jQuery.active == 0"))
