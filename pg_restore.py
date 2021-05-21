import configparser
import sys
import datetime
import subprocess

from configparser import Error, NoSectionError
from subprocess import PIPE, Popen, CalledProcessError


__author__ = "David Morais"
__credits__ = ["David Morais"]
__version__ = "1.0.1-SNAPSHOT"
__maintainer__ = "David Morais"
__email__ = "moraisdavid8@gmail.com"
__status__ = "Dev"

def get_remote_db_credentials():
    """This methods gets the remote database credentials from database.ini file

    Returns:
        dict: Returns the credentials for the remote database on a dict.
    """

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

    except Error as error:

        print('Error during get credentials: ' + error)

    except NoSectionError as error:

        print('Especified section not found at database.ini: ' + error)

    finally:

        config.clear()

def do_pg_restore(host, user, passwd, datname, dump_file):
    """Execute the pg_restore command on the remote database.

    Args:
        host (String): FQDN (Fully Qualified Domain Name) of the remote host that contains the database.
        user (String): user that owns the database
        passwd (String): passord for the owner user
        datname (String): remote database name
        dump_file (String): file path to the dump file get at the remotehost.py script

    Returns:
        boolean: Returns the pg_restore result status.
    """

    pg_restore_command = f'pg_restore --host={host} ' \
            f'--username={user} ' \
            f'--no-owner ' \
            f'--format=d ' \
            f'--dbname={datname} ' \
            f'{dump_file} '

    print(f"Comando executado: {pg_restore_command}")

    success = True

    try:

        command = Popen(pg_restore_command, shell=True, env={'PGPASSWORD': passwd})

        command.wait()

    except CalledProcessError as e:
        
        success = False
        print(e)


    return success

def main():
    """The main methos that execute the entire routine
    """

    credentials = get_remote_db_credentials()
    user = credentials['user']
    database = credentials['db']
    address = credentials['address']
    password = credentials['password']

    dump_file_path = 'sapiencia'

    print('Restaurando dump em na nova instancia')
    restore_success = do_pg_restore(address, user, password, database, dump_file_path)
    if restore_success:
        print("Banco restarado com sucesso!")
    else:
        print("Erros ocorreram durante o restore")

if __name__ == "__main__":
    main()
