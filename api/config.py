HUB_URL = 'http://hub:4444/wd/hub'
CAPTCHA_RETRIES = 10


# Auth

KEY_ANTIGATE = ''

WORDSTAT_LOGIN = ''
WORDSTAT_PASSWD = ''

try:
    from .config_prod import *
except ImportError:
    pass
