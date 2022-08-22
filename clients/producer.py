import pika
import ssl


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

    def publish(self, routing_key, body):
        self.channel.basic_publish(exchange='messages', routing_key=routing_key, body=body)
        print(" [x] Sent to " + routing_key + " Message: " + body)
        self.connection.close()
