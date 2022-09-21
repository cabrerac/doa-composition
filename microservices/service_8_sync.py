from flask import Flask, make_response, request
import time
from logic import util


description = util.read_service_description('./description/service_8.json')


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_8_sync', methods=['GET', 'POST'])
def service_8_sync():
    try:
        parameters = request.get_json()
        ms = 0.0039
        time.sleep(ms)
        outputs = description['outputs']
        for output in outputs:
            output['value'] = 'Output value from ' + description['name']
        return make_response({'res': 'Response from ' + description['name'] + '_sync', 'outputs': outputs})
    except:
        return make_response({'res': 'Service exception!!!', 'outputs': []})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
