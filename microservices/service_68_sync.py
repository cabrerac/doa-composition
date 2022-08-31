from flask import Flask, make_response, request
import time

# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_68', methods=['GET', 'POST'])
def service_68():
    try:
        parameters = request.get_json()
        ms = 0.0059
        time.sleep(ms)
        return make_response({'res': 'Response from service_68'})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
