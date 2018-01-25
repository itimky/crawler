import tempfile

import requests
from flask_restful import reqparse, fields, marshal_with, Resource, abort

from . import utils
from api.config import WORDSTAT_LOGIN, WORDSTAT_PASSWD, CAPTCHA_RETRIES


WORDSTAT_URL = 'https://wordstat.yandex.ru/#!/%s?words=%s'


WORDSTAT_FIELDS = {
    'soup': fields.String
}


def get_query_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('query', type=str, location='args', required=True)
    return parser


class WordstatWords(Resource):
    @marshal_with(WORDSTAT_FIELDS)
    def get(self):
        args = get_query_parser().parse_args()
        return {'soup': get_wordstat('words', args.query)}


class WordstatHistory(Resource):
    @marshal_with(WORDSTAT_FIELDS)
    def get(self):
        args = get_query_parser().parse_args()
        return {'soup': get_wordstat('history', args.query)}


def get_wordstat(type_, query):
    with utils.get_chrome_ipv4() as driver:
        # Fake page to set cookies
        driver.get('https://wordstat.yandex.ru/404')
        utils.load_cookies(driver, 'wordstat.pkl')
        driver.get(WORDSTAT_URL % (type_, query))
        wordstat_login(driver)
        attempt = 0
        while is_wordstat_captcha(driver) and attempt < CAPTCHA_RETRIES:
            attempt += 1
            wordstat_captcha(driver)
        utils.save_cookies(driver, 'wordstat.pkl')
        if attempt == CAPTCHA_RETRIES:
            abort(500, error='max captcha retries (%s)' % (CAPTCHA_RETRIES,))
        return utils.get_soup(driver.page_source)


def wordstat_login(driver):
    form = driver.find_elements_by_xpath(
        '//form[contains(@class, "b-domik_type_popup") ' +
        'and not(contains(@class, "i-hidden"))]')
    if form:
        form = form[0]
        login = form.find_element_by_name('login')
        passwd = form.find_element_by_name('passwd')
        login.send_keys(WORDSTAT_LOGIN)
        passwd.send_keys(WORDSTAT_PASSWD)
        passwd.submit()
    utils.wait_for_jquery_ajax(driver)


def is_wordstat_captcha(driver):
    return len(driver.find_elements_by_xpath(
        '//div[contains(@class, "i-popup_visibility_visible")]')) > 0


def wordstat_captcha(driver):
    div = driver.find_element_by_xpath(
        '//div[contains(@class, "i-popup_visibility_visible")]')
    temp = tempfile.NamedTemporaryFile(suffix='.gif')
    img = div.find_element_by_xpath('//img[@class="b-popupa__image"]')
    img_src = img.get_attribute('src')
    try:
        response = requests.get(img_src)
        response.raise_for_status()
        for chunk in response:
            temp.file.write(chunk)
        temp.file.close()

    except (requests.RequestException, requests.HTTPError):
        return

    try:
        form_input = div.find_element_by_xpath(
            '//td[contains(@class, "b-page__captcha-input-td")]' +
            '//input[@class="b-form-input__input"]')
        text = utils.solve_captcha(img_filename=temp.name)
        form_input.clear()
        form_input.send_keys(text)
        form_input.submit()
        utils.wait_for_jquery_ajax(driver)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(driver.page_source)
        print(e)
