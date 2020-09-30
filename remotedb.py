import requests
from requests.auth import HTTPBasicAuth
import json
import configparser
import sys
from pathlib import Path
from os import environ, path
from dotenv import load_dotenv


__author__ = "David Morais"
__credits__ = ["David Morais"]
__version__ = "1.0.1-SNAPSHOT"
__maintainer__ = "David Morais"
__email__ = "moraisdavid8@gmail.com"
__status__ = "Dev"

URL_BASE = 'https://customer.elephantsql.com/api'


def get_elephansql_api_key():
    """This methods gets the api key from .env file

    Returns:
        tuple: Returns a tuple in the format accept by the API
    """
    try:

        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))

        API_KEY = environ.get('ELEPHANTSQL_API_KEY')
        AUTH_INFO = ('', API_KEY)
        return AUTH_INFO

    except FileNotFoundError as e:

        print(e)
        sys.exit(2)


def list_instances(AUTH_INFO):
    """This function gets de list of the intances currently avaiable at the ELEPHANTSQL team.

    Returns:
        dict: Returns de json reponse from api method
    """

    ENDPOINT = f'{URL_BASE}/instances'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def get_instance_info(instance_id, AUTH_INFO):
    """This method get information about an specific instance by her id.

    Arguments:
        instance_id {interger}: Instance's id that wants to get information
        AUTH_INFO {tuple}: Tuple contains the information for authentication on the ELEPHANTSQL API.

    Returns:
        dict: Returns de json reponse from api method
    """

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.get(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def delete_instance(instance_id, AUTH_INFO):
    """This method deletes  an specific instance by her id.

    Arguments:
        instance_id {interger}: Instance's id that wants to delete
        AUTH_INFO {tuple}: Tuple contains the information for authentication on the ELEPHANTSQL API.

    Returns:
        string: Returns de json reponse from api method
    """

    ENDPOINT = f'{URL_BASE}/instances/{instance_id}'

    response = requests.delete(ENDPOINT, auth=AUTH_INFO, verify=True)

    if response.status_code == 204:
        message = f'Instancia ({instance_id}) deletada com sucesso.'
        return message


def create_instance(name, aws_region, AUTH_INFO):
    """This method deletes  an specific instance by her id.

    Arguments:
        name {string}: User name to concatenate in the instance name when created.
        aws_region {string}: AWS region for instance deploy.
        AUTH_INFO {tuple}: Tuple contains the information for authentication on the ELEPHANTSQL API.

    Returns:
        dict: Returns de json reponse from api method
    """

    ENDPOINT = f'{URL_BASE}/instances'
    params = f'name=sapiencia-{name}&plan=turtle&region=amazon-web-services::{aws_region}&tags=teste'

    response = requests.post(ENDPOINT, auth=AUTH_INFO,
                             params=params, verify=True)

    if response.status_code == 200:
        content = response.json()
        return content


def renew_instance(user_name, AUTH_INFO):
    """This method execute routine of get a existent instance, delete it and create a new one for the user.

    Arguments:
        user_name {string}: User name to concatenate in the instance name when created.
        AUTH_INFO {tuple}: Tuple contains the information for authentication on the ELEPHANTSQL API.

    Returns:
        dict: Return the information about the recentily created instance on the json format.
    """

    print('Listando instâncias atuais')
    current_instances = list_instances(AUTH_INFO)

    print(f'Bucando instancia de {user_name}')
    target = next(
        (instance for instance in current_instances if f'{user_name}' in instance['name']), None)

    if target == None:

        print(f'{user_name} não possui uma instância atualmente')
        print(f'Criando instância sapiencia-{user_name}')
        new_instance = create_instance(user_name, 'sa-east-1', AUTH_INFO)
        return new_instance

    else:

        print(f'{user_name} já possui uma instância atualmente')
        print('Deletando instancia atual...')
        message = delete_instance(target['id'], AUTH_INFO)
        print(message)

        print(f'Criando nova instância sapiencia-{user_name}')
        new_instance = create_instance(user_name, 'sa-east-1', AUTH_INFO)

        return new_instance


def main(user_name):
    """This is the manin method that execute the entire routine.

    Args:
        user_name (String): Username from the user thats running the script.
    """
    
    AUTH_INFO = get_elephansql_api_key()

    try:

        new_instance = renew_instance(user_name, AUTH_INFO)

        instance_id = new_instance['id']
        instance_url = new_instance['url']
        instance_address = instance_url.split("@")[1].split(":")[0]
        instance_user_db = instance_url.split('//')[1].split('@')[0].split(':')[0]
        instance_passwd = instance_url.split('//')[1].split('@')[0].split(':')[1]

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
