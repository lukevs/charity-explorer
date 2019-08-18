from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from search import search_charities

PORT = 8778
app = Flask(__name__)

CORS(app) # TODO: remove for a prod deployment

def build_error_response(message):
    error_data = {
        'error': message
    }

    return jsonify(error_data), 400

@app.route('/hello', methods=['GET'])
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
    results = search_charities(query).to_dict('records')

    return jsonify({
        'results': results,
    })


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
