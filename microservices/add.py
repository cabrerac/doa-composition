from flask import Flask, make_response, request


app = Flask('__name__')


@app.route('/doa_composition/add', methods=['GET', 'POST'])
def add():
    parameters = request.get_json()
    s1 = parameters['s1']
    s2 = parameters['s2']
    return make_response({'res': s1 + s2})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
