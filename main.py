import requests
from deployment import deploy_to_aws


add_service = {'name': 'doa-composition-add-service', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
               'path': '/doa_service_composition/add', 'priority': 1, 'count': 1}
square_service = {'name': 'doa-composition-square-service', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
                  'path': '/doa_service_composition/add', 'priority': 2, 'count': 1}
home_service = {'name': 'doa-composition-home-service', 'imageUrl': '', 'port': 5000, 'cpu': 256, 'memory': 512,
                  'path': '/doa_service_composition/home', 'priority': 2, 'count': 1}
services = [home_service]

deploy_to_aws.deploy_services('doa-resources-template.yml','doa-service-template.yml',services)

#base_url = 'http://doa-composition-load-balancer-692124022.eu-west-2.elb.amazonaws.com:80'

#url = base_url + '/doa_sc/get_data'
#response = requests.get(url)
#print(response.content)

#url = base_url + '/doa_service_composition/square'
#parameters = {'s1': 6, 's2': 6}
#response = requests.post(url, json=parameters)
#print(response.json())
