from flask import Flask, make_response
import logic.home_function as logic

# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/home', methods=['GET', 'POST'])
def home():
    return make_response({'res': logic.home_function()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
