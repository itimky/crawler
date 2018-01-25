from flask import Flask, Blueprint
from flask_restful import Api, output_json

from .google import Google
from .wordstat import WordstatWords, WordstatHistory


def create_api(blueprint):
    api = Api(blueprint)
    api.representations = {
        'application/json; charset=utf-8': output_json,
    }

    api.add_resource(Google, '/google', endpoint='google')
    api.add_resource(WordstatWords, '/wordstat/words',
                     endpoint='wordstat_words')
    api.add_resource(WordstatHistory, '/wordstat/history',
                     endpoint='wordstat_history')

    return api


def create_app():
    app = Flask(__name__)
    app.config.from_object('api.config')

    api_bp = Blueprint('crawler', __name__)
    create_api(api_bp)

    app.register_blueprint(api_bp)
    return app


application = create_app()
