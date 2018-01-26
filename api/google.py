from flask_restful import reqparse, Resource

from . import utils


RETRIES = 16
GOOGLE_URL = 'https://www.google.ru/search?num=100&q=%s&near=%s'


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
        for i in range(RETRIES):
            with utils.get_chrome_ipv6() as driver:
                driver.get(link)
                if 'IndexRedirect?' not in driver.current_url \
                        and 'google.com/sorry/' not in driver.current_url:
                    return {'soup': utils.get_soup(driver.page_source)}
