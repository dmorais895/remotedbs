import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

URL_BASE = 'https://customer.elephantsql.com/api'
API_KEY = config.get('config', 'api_key')
AUTH_INFO = ('', API_KEY)

def list_instances():

    ENDPOINT = f'{URL_BASE}/instances'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content

def get_instace_info(instance_id):

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content

def delete_instance(instance_id):

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.delete(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        message = f'Instancia({instance_id}) deletada com sucesso'
        return message

def create_instance(name, aws_region='sa-east-1'):

    ENDPOINT = f'{URL_BASE}/instances'
    params = f'name={name}&plan=turtle&region=amazon-web-services::{aws_region}'

    response = requests.post(ENDPOINT, auth=AUTH_INFO, params=params, verify=True)

    print(response.status_code)
    if response.status_code == 200:
        content = response.json()
        return content

def main(user_name):

        

    

if __name__ == "__main__":
    main()