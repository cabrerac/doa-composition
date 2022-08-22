from flask import Flask, make_response, request
import logic.util as util
import logic.square_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import json

rabbit_credentials_file = 'rabbit-mq.yaml'


def callback(ch, method, properties, body):
    p = None
    message = json.loads(body)
    req_id = message['req_id']
    next_topic = message['next_topic']
    parameters = message['parameters']
    for parameter in parameters:
        if parameter['name'] == 'p':
            p = parameter['value']
    res = logic.square_function(p)
    message_dict = {
        'req_id': req_id, 'user_topic': 'user.response', 'desc': 'message from square!!!',
        'next_topic': 'user.response', 'res': logic.square_function(p)
    }
    message_json = json.dumps(message_dict, indent=4)
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_json)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service.square', callback)
consumer_thread.start()


# Flask interface
app = Flask(__name__)


@app.route('/doa_composition/square_async', methods=['GET', 'POST'])
def square():
    try:
        parameters = request.get_json()
        p = parameters['p']
        return make_response({'res': logic.square_function(p)})
    except:
        return make_response({'res': 'Service exception!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
