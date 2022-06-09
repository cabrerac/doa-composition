from flask import Flask, make_response


app = Flask('__name__')


@app.route('/doa_service_composition/home', methods=['GET', 'POST'])
def home():
    return make_response({'res': 'Hello world!!!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


"""@app.route("/doa_composition/request_service", methods=["GET", "POST", "PUT", "DELETE"])
def request_service():
    parameters = request.get_json()
    print("Publishing message...")
    producer = kafka_broker.kafka_producer('add', parameters)


def add(message):
    topic_name = 'add'
    # obtain the last offset value
    consumer, tp = kafka_broker.kafka_consumer(topic_name)
    consumer.seek_to_end(tp)
    lastOffset = consumer.position(tp)
    consumer.seek_to_beginning(tp)
    emit('kafkaconsumer1', {'data': ''})
    for message in consumer:
        print(message)
        emit('kafkaconsumer', {'data': message.value.decode('utf-8')})
        if message.offset == lastOffset - 1:
            break
    consumer.close()


def product(message):
    res = {}
    return res"""
