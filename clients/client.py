import requests


def make_request(external_url, service_path, parameters):
    url = external_url + service_path
    response = requests.post(url, json=parameters)
    return response.json()
