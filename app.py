import dataclasses
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from charity import CharityIndex


app = Flask(__name__)
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CORS(app) # TODO: remove for a prod deployment

DEFAULT_INDEX_PATH = './index'
charity_index = CharityIndex.load(DEFAULT_INDEX_PATH)


def build_error_response(message):
    error_data = {
        'error': message
    }

    return jsonify(error_data), 400

@app.route('/', methods=['GET'])
def welcome():
    return jsonify({
        'result': 'Welcome to YouCharity!'
    })

@app.route('/search', methods=['POST'])
def search():
    if request.json is None:
        return build_error_response(
            'Missing json',
        )

    if 'query' not in request.json:
        return build_error_response(
            'Missing query key',
        )

    query = request.json['query']
    rank = request.args.get('rank') == 'true'

    results = charity_index.search(
        query,
        rank_with_next_sentence_prediction=rank,
    )

    results_as_dict = [
        dataclasses.asdict(charity)
        for charity in results
    ]

    return jsonify({
        'results': results_as_dict,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
