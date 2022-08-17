from flask import Flask, make_response, request
import logic.add_function as logic

# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/add', methods=['GET', 'POST'])
def add():
    parameters = request.get_json()
    a = parameters['s1']
    b = parameters['s2']
    return make_response({'res': logic.add_function(a, b)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
