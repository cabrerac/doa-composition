from flask import Flask, make_response, request
import time

# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_72', methods=['GET', 'POST'])
def service_72():
    try:
        parameters = request.get_json()
        ms = 0.0039
        time.sleep(ms)
        return make_response({'res': 'Response from service_72'})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
