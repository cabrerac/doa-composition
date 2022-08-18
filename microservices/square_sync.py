from flask import Flask, make_response, request
import logic.square_function as logic


# Flask interface
app = Flask(__name__)


@app.route('/doa_composition/square', methods=['GET', 'POST'])
def square():
    try:
        parameters = request.get_json()
        p = parameters['p']
        return make_response({'res': logic.square_function(p)})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
