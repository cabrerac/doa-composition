from flask import Flask, make_response
import logic.util as util
import logic.home_function as logic
from clients.producer import Producer
from clients.consumer import Consumer
import json


rabbit_credentials_file = 'rabbit-mq.yaml'


def callback(ch, method, properties, body):
    message = json.loads(body)
    req_id = message['req_id']
    next_topic = message['next_topic']
    message_dict = {
        'req_id': req_id, 'user_topic': 'user.response', 'desc': 'response from home!!!',
        'next_topic': 'user.response',
        'res': logic.home_function()
    }
    credentials = util.read_rabbit_credentials(rabbit_credentials_file)
    producer = Producer(credentials)
    producer.publish(next_topic, message_dict)


credentials = util.read_rabbit_credentials(rabbit_credentials_file)
consumer_thread = Consumer(credentials, 'service.home', callback)
consumer_thread.start()


# Flask interface
app = Flask('__name__')


@app.route('/doa_composition/home_async', methods=['GET', 'POST'])
def home():
    return make_response({'res': logic.home_function()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
