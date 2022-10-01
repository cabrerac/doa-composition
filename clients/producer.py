import pika
import ssl
import json


class Producer:

    def __init__(self, credentials):
        rabbit_url = credentials['rabbitmq_url']
        rabbit_port = credentials['port']
        rabbit_virtual_host = credentials['virtual_host']
        rabbit_credentials = pika.PlainCredentials(credentials['username'], credentials['password'])
        rabbit_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        rabbit_parameters = pika.ConnectionParameters(host=rabbit_url, port=rabbit_port,
                                                      virtual_host=rabbit_virtual_host, credentials=rabbit_credentials,
                                                      ssl_options=pika.SSLOptions(rabbit_context))
        self.connection = pika.BlockingConnection(rabbit_parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='messages', exchange_type='topic', durable=True)
        self.channel.confirm_delivery()

    def publish(self, routing_key, body):
        try:
            body_json = json.dumps(body, indent=4)
            self.channel.basic_publish(exchange='messages', routing_key=routing_key, body=body_json, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE), mandatory=True)
            self.connection.close()
            print(" [x] Sent to " + routing_key + " Message: " + body['desc'])
            return True
        except pika.exceptions.UnroutableError:
            return False
