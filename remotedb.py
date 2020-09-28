import requests
from requests.auth import HTTPBasicAuth
import json
import configparser
import sys
from pathlib import Path


# config = configparser.ConfigParser()
# config.read('config.ini')

URL_BASE = 'https://customer.elephantsql.com/api'

print(AUTH_INFO)

def list_instances(AUTH_INFO):

    ENDPOINT = f'{URL_BASE}/instances'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def get_instance_info(instance_id, AUTH_INFO):

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def delete_instance(instance_id, AUTH_INFO):

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.delete(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 204:
        message = f'Instancia ({instance_id}) deletada com sucesso.'
        return message


def create_instance(name, aws_region='sa-east-1', AUTH_INFO):

    ENDPOINT = f'{URL_BASE}/instances'
    params = f'name=sapiencia-{name}&plan=turtle&region=amazon-web-services::{aws_region}&tags=teste'

    response = requests.post(ENDPOINT, auth=AUTH_INFO,
                             params=params, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def renew_instance(user_name, AUTH_INFO):

    print('Listando instâncias atuais')
    current_instances = list_instances(AUTH_INFO)

    print(f'Bucando instancia de {user_name}')
    target = next(
        (instance for instance in current_instances if f'{user_name}' in instance['name']), None)

    if target == None:

        print(f'{user_name} não possui uma instância atualmente')
        print(f'Criando instância sapiencia-{user_name}')
        new_instance = create_instance(user_name, AUTH_INFO)
        return new_instance

    else:

        print(f'{user_name} já possui uma instância atualmente')
        print('Deletando instancia atual...')
        message = delete_instance(target['id'], AUTH_INFO)
        print(message)

        print(f'Criando nova instância sapiencia-{user_name}')
        new_instance = create_instance(user_name, AUTH_INFO)

        return new_instance


def main(user_name):

    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config.get('config', 'api_key')
    AUTH_INFO = ('', API_KEY)

    try:

        new_instance = renew_instance(user_name, AUTH_INFO)

        instance_id = new_instance['id']
        instance_url = new_instance['url']
        instance_address = instance_url.split("@")[1].split(":")[0]
        instance_user_db = instance_url.strip('postgres://').split(':')[0]
        instance_passwd = instance_url.strip(
            'postgres:\/\/\/').split("@")[0].split(":")[1]
        print(instance_user_db)
        parser = configparser.ConfigParser()
        parser.add_section('database')
        parser.set('database', 'id', f'{instance_id}')
        parser.set('database', 'url', f'{instance_url}')
        parser.set('database', 'address', f'{instance_address}')
        parser.set('database', 'user', f'{instance_user_db}')
        parser.set('database', 'db', f'{instance_user_db}')
        parser.set('database', 'password', f'{instance_passwd}')

        new_config_file = Path('database.ini')
        parser.write(new_config_file.open('w'))

    except configparser.ParsingError as e:

        print(e)
        sys.exit(1)

    except FileExistsError as e:
        print(e)
        sys.exit(2)

    except IOError as e:

        print(e)
        sys.exit(3)


if __name__ == "__main__":

    main(sys.argv[1])
