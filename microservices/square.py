from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


@app.route('/doa_service_composition/square')
def square():
    parameters = request.get_json()
    p = parameters['p']
    return make_response({'data': p * p})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
