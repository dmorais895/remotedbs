import configparser
import sys

from os import environ, path
from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException
from .log import logger

def get_remote_db_credentials():

    config = configparser.ConfigParser()

    try:

        config.read('database.ini')

        credentials = {
            "url": config.get('database', 'url'),
            "address": config.get('database', 'address'),
            "user": config.get('database', 'user'),
            "db": config.get('database', 'db'),
            "password": config.get('database', 'password')
        }

        return credentials

    except FileNotFoundError as e:

        print(e)
        sys.exit(1)


def get_backup_host_credentials():

    try:

        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))

        credentials = {
            "host": environ.get('POSTGRES_HOST'),
            "user": environ.get('POSTGRES_USER'),
            "ssh_key_path": environ.get('SSH_KEY'),
            "remote_backup_path": environ.get('REMOTE_PATH'),
            "ssh_port": environ.get('REMOTE_SSH_PORT')
        }

        return credentials

    except FileNotFoundError as e:

        print(e)
        sys.exit(2)


def connect_to_backup_host(host, user, ssh_key_path, ssh_port)

    try:
        
        scp_client = SSHClient()
        scp_client.load_system_host_keys()
        scp_client.set_missing_host_key_policy(AutoAddPolicy())
        scp_client.connect(
            host,
            username=user,
            port=ssh_port,
            key_filename=ssh_key_path,
            look_for_keys=True,
            timeout=5000
        )

        scp = SCPClient(scp_client.get_transport())

    except AuthenticationException as e:
        print(f'Authentication failed: {e}')
        sys.exit(3)
    
    return scp_client

