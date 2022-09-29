from flask import Flask, make_response, request
import time
from logic import util


description = util.read_service_description('./description/service_31.json')


# flask interface
app = Flask('__name__')


# microservice endpoint
@app.route('/doa_composition/service_31_sync', methods=['GET', 'POST'])
def service_31_sync():
    try:
        parameters = request.get_json(silent=True)
        if parameters == None:
            parameters = {}
        ms = 0.0054
        inputs = []
        if 'inputs' in parameters:
            inputs = parameters['inputs']
        time.sleep(ms)
        outputs = description['outputs']
        for output in outputs:
            output['value'] = 'Output value from ' + description['name']
        return make_response({'res': 'Response from ' + description['name'] + '_sync', 'outputs': outputs})
    except Exception as ex:
        return make_response({'res': 'Service exception ' + ex + '!!!', 'outputs': []})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
