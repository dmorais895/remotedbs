import configparser
import sys
import datetime
import tarfile

from os import environ, path
from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException


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

    finally:

        config.clear()


def get_remote_host_credentials():

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


def connect_to_backup_host(host, user, ssh_key_path, ssh_port):

    try:

        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(
            host,
            username=user,
            port=ssh_port,
            key_filename=ssh_key_path,
            look_for_keys=True,
            timeout=5000
        )

        scp_client = SCPClient(ssh_client.get_transport())

    except AuthenticationException as e:

        print(f'Authentication failed: {e}')
        raise e
        sys.exit(3)

    return ssh_client, scp_client


def disconnect_from_backup_host(ssh_client, scp_client):

    if ssh_client:
        ssh_client.close()

    if scp_client:
        scp_client.close()

    return ssh_client, scp_client


def get_date():

    date = datetime.date.today() - datetime.timedelta(days=1)

    target_date = date.strftime("%Y%m%d")

    return target_date


def execute_remote_command(command, ssh_client):

    stdin, stdout, stderr = ssh_client.exec_command(command)

    stdout.channel.recv_exit_status()

    response = stdout.readlines()

    for lines in response:
        print(f'INPUT: {command} - OUTPUT: {stdout}')


def get_file_from_remote_host(filename, scp_client):

    try:

        scp_client.get(filename, local_path='./')

    except SCPException as e:

        raise e


def umcompress_file(compressed_file):

    uncrompress = tarfile.open(compressed_file, "r:gz")

    uncrompress.extractall()

    uncrompress.close()


def main(backup_name):

    print('Getting remote host credentials')
    remote_host_credentials = get_remote_host_credentials()
    print(remote_host_credentials)

    date = get_date()

    try:

        ssh_client, scp_client = connect_to_backup_host(
            remote_host_credentials['host'],
            remote_host_credentials['user'],
            remote_host_credentials['ssh_key_path'],
            remote_host_credentials['ssh_port']
        )

        backup_file_name = f'{backup_name}_{date}'
        remote_file_name = f'{backup_file_name}.tar.gz'
        print(remote_file_name)
        print(remote_host_credentials.get('remote_backup_path'))

        print('Creating remote tar.gz from target directory at the remote host')
        remote_command = f'cd {remote_host_credentials["remote_backup_path"]} && tar -czf $HOME/{remote_file_name}.tar.gz {backup_file_name}'
        print(f'Executing remote command: {remote_command}')
        execute_remote_command(remote_command, ssh_client)

        print('Getting tar file from remote host')
        get_file_from_remote_host(remote_file_name, scp_client)

        print('Uncompressing recived file locally')
        umcompress_file(remote_file_name)

    finally:

        ssh_client.close()
        scp_client.close()


if __name__ == "__main__":

    main('sapiencia')
