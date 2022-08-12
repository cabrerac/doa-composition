import pika
import ssl


class Producer:

    def __init__(self, credentials, queue):
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
        self.channel.queue_declare(queue=queue, durable=True)

    def publish(self, routing_key, body):
        self.channel.basic_publish(exchange='', routing_key=routing_key, body=body)
        print(" [x] Sent " + body)
        self.connection.close()
