from flask import Flask, make_response, request
import pika
import time
import logic.util as util
import logic.add_function as logic


# Listening for RabbitMQ Messages
sleepTime = 10
time.sleep(30)

credentials = util.read_rabbit_credentials('rabbit-mq.yaml')
host = credentials['host']
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()
channel.queue_declare(queue='task_square', durable=True)


def _callback(ch, method, properties, body):
    msg = body.decode()
    if msg == 'hey':
        print("hey there")
    elif msg == 'hello':
        print("well hello there")
    else:
        print("sorry i did not understand ", body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_square', on_message_callback=_callback)
channel.start_consuming()


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
