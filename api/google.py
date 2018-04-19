import requests
from flask_restful import reqparse, Resource
from fake_useragent import UserAgent

from . import utils


UA = UserAgent()
HTTP_429_TOO_MANY_REQUESTS = 429
RETRIES = 1
GOOGLE_URL = 'https://www.google.ru/search?num=100&q=%s&near=%s'
PROXIES = {
    'http': 'http://proxy:5050',
    'https': 'http://proxy:5050',
}


def get_query_parser():
    """
    @apiDefine GoogleQueryParams

    @apiParam (QueryParam) {String} query Search query.
    @apiParam (QueryParam) {String} [region=Москва] Region.
    """
    parser = reqparse.RequestParser()
    parser.add_argument('query', type=str, location='args', required=True)
    parser.add_argument('region', type=str, location='args', default='Москва')
    return parser


class Google(Resource):
    @staticmethod
    def get():
        """
        @api {get} /google Get Google
        @apiVersion 0.1.0
        @apiName GetGoogle
        @apiGroup Google

        @apiUse GoogleQueryParams

        @apiSuccess {String} soup Soup.
        """
        args = get_query_parser().parse_args()
        link = GOOGLE_URL % (args.query, args.region)
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': UA.random
        })

        for i in range(RETRIES):
            r = requests.get(link, proxies=PROXIES, headers=headers)
            if 'google.com/sorry/' not in r.url:
                    return {'soup': utils.get_soup(r.text)}
        return {'error': 'Still captcha after %s retries' % RETRIES},\
            HTTP_429_TOO_MANY_REQUESTS
