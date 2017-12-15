import pickle
from os import path

from antigate import AntiGate
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

from .config import HUB_URL, KEY_ANTIGATE


def get_chrome():
    driver = webdriver.Remote(
        command_executor=HUB_URL,
        desired_capabilities=DesiredCapabilities.CHROME)
    return driver


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
