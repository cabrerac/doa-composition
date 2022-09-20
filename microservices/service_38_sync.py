from flask import Flask, make_response, request
import time
from logic import util


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/service_38_sync', methods=['GET', 'POST'])
def service_38_sync():
    try:
        parameters = request.get_json()
        ms = 0.0081
        time.sleep(ms)
        description = util.read_service_description('./description/service_38.json')
        outputs = description['outputs']
        for output in outputs:
            output['value'] = 'Output value from service_38'
        return make_response({'res': 'Response from service_38_sync', 'outputs': outputs})
    except:
        return make_response({'res': 'Service exception!!!', 'outputs': []})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
