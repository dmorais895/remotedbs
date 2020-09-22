import requests
from requests.auth import HTTPBasicAuth
import json
import configparser
import sys

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

    if response.status_code == 204:
        message = f'Instancia ({instance_id}) deletada com sucesso.'
        return message

def create_instance(name, aws_region='sa-east-1'):

    ENDPOINT = f'{URL_BASE}/instances'
    params = f'name=sapiencia-{name}&plan=turtle&region=amazon-web-services::{aws_region}'

    response = requests.post(ENDPOINT, auth=AUTH_INFO, params=params, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content

def renew_instance(user_name):

    print('Listando instâncias atuais')
    current_instances = list_instances()

    print(f'Bucando instancia de {user_name}')
    target = next((instance for instance in current_instances if f'{user_name}' in instance['name']), None)

    if target == None:
        
        print(f'{user_name} não possui uma instância atualmente')
        print(f'Criando instância sapiencia-{user_name}')
        new_instance = create_instance(user_name)
        return new_instance
    
    else:
        
        print(f'{user_name} já possui uma instância atualmente')
        print('Deletando instancia atual...')
        message = delete_instance(target['id'])
        print(message)
        
        print(f'Criando nova instância sapiencia-{user_name}')
        new_instance = create_instance(user_name)

        return new_instance


def main(argv):

    user_name = argv

    try:

        new_instance = renew_instance(user_name)
        print(new_instance)

    except Exception as e:

        print(e)
        sys.exit(1)

if __name__ == "__main__":

    main('david')