import configparser
import sys
import datetime
import tarfile

from os import environ, path
from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException
from tarfile import ExtractError, ReadError

__author__ = "David Morais"
__credits__ = ["David Morais"]
__version__ = "1.0.1-SNAPSHOT"
__maintainer__ = "David Morais"
__email__ = "moraisdavid8@gmail.com"
__status__ = "Dev"

def get_remote_host_credentials():
    """Get credentials of the host that helds the dumps for the database restore script.

    Returns:
        dict: Returns a dict with de credentials for connect on the host with SSH/SCP.
    """

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
    """This methos execute de SSH/SCP connection on the remote host that helds the dump files.

    Args:
        host (String): FQDN (Fully Qualified Domain Name) of the remote host that contains the dump files.
        user (String): Username to connect with SSH/SCP
        ssh_key_path (String): Path to the private key for the connection
        ssh_port (String): SSH protocol port open at the host

    Returns:
        Object (SSHClient): SSHClient object to interact with the remote host.
        Object (SCPClient): SCPClient object to interact with the remote host.
    """

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
        sys.exit(3)

    return ssh_client, scp_client


def disconnect_from_backup_host(ssh_client, scp_client):
    """This method closes the SSH/SCP connection to the remote host

    Args:
        ssh_client (SSHClient): SSHClient object obtained from the connect_to_backup_host
        scp_client (SCPClient): SCPClient object obtained from the connect_to_backup_host
    Returns:
        Object (SSHClient): SSHClient object to interact with the remote host.
        Object (SCPClient): SCPClient object to interact with the remote host.
    """

    if ssh_client:
        ssh_client.close()

    if scp_client:
        scp_client.close()

    return ssh_client, scp_client


def get_date():
    """This methos gets the yerterdate date on the format: YYYYMMDD

    Returns:
        String: yerterday date on the format: YYYYMMDD
    """

    date = datetime.date.today() - datetime.timedelta(days=1)

    target_date = date.strftime("%Y%m%d")

    return target_date


def execute_remote_command(command, ssh_client):
    """This method execute command on the remote host:

    Args:
        command (String): Command to be executed on the remote host 
        ssh_client (SSHClient): SSHCLient object to connects on the remote host.
    """

    stdin, stdout, stderr = ssh_client.exec_command(command)

    stdout.channel.recv_exit_status()

    response = stdout.readlines()

    for lines in response:
        print(f'INPUT: {command} - OUTPUT: {stdout}')


def get_file_from_remote_host(filename, scp_client):
    """This methos gets a file from the remote host via SCP connection.

    Args:
        filename (String): The name of the file to be geted.
        scp_client (SCPClient): SCPClient object to use on the scp connection.

    Raises:
        e: SCPException if the connection goes wrong.
    """

    try:

        scp_client.get(filename, local_path='./')

    except SCPException as e:

        raise e


def decompress_file(compressed_file):
    """This methos decompress a file locally

    Args:
        compressed_file (String): The name of the compressed file.

    Returns:
        boolean: Returns true if dont get an exception during the extraction of the file.
    """

    try:

        uncrompress = tarfile.open(compressed_file, "r:gz")

        uncrompress.extractall()

        return True

    except ReadError as error:

        print('Error reading the target file:' + error)

    except ExtractError as error:

        print('Error during de file extract: ' + error)
        return False

    finally:

        uncrompress.close()


def main(backup_name):
    """The main methos that execute the entire routine

    Args:
        backup_name (String): Name of the dump file at the remote host.
    """

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

        backup_file_dir = f'{backup_name}_{date}'
        print(backup_file_dir)
        remote_file_name = f'{backup_name}.tar.gz'
        print(remote_file_name)

        print(
            f'Target file: {remote_host_credentials["remote_backup_path"]}/{backup_file_dir}')

        print('Creating remote tar.gz from target directory at the remote host')
        remote_command = f'cd {remote_host_credentials["remote_backup_path"]}/{backup_file_dir} && tar -czf $HOME/{remote_file_name} {backup_name}'
        print(f'Executing remote command: {remote_command}')
        execute_remote_command(remote_command, ssh_client)

        print('Getting tar file from remote host')
        get_file_from_remote_host(remote_file_name, scp_client)

        print('Decompressing file locally')
        if decompress_file(remote_file_name):
            print('Successfully decompressed file')

    except Exception as e:

        print(e)

    finally:

        print('Closing connections')
        ssh_client.close()
        scp_client.close()


if __name__ == "__main__":

    main('sapiencia')
