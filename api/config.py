HUB_URL = 'http://selenoid:4444/wd/hub'
CAPTCHA_RETRIES = 10


# Auth

KEY_ANTIGATE = ''

WORDSTAT_LOGIN = ''
WORDSTAT_PASSWD = ''


BROWSERS = {
    'chrome': ['64.0', '63.0', '62.0', '61.0', '60.0'],
    'firefox': ['58.0', '57.0']
}


try:
    from .config_prod import *
except ImportError:
    pass
