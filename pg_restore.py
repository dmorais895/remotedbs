import configparser
import sys
import datetime
import subprocess

from configparser import Error, NoSectionError
from subprocess import PIPE, Popen, CalledProcessError


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

    except Error as error:

        print('Error during get credentials: ' + error)

    except NoSectionError as error:

        print('Especified section not found at database.ini: ' + error)

    finally:

        config.clear()

def do_pg_restore(host, user, passwd, datname, dump_file):

    pg_restore_command = [
        'pg_restore',
        f'-U {user}',
        f'--no-password',
        f'-h {host}',
        f'-j 2',
        '--no-owner',
        f'-Fd',
        f'-d {datname}',
        dump_file
    ]

    print(pg_restore_command)

    success = True

    try:

        command = Popen(pg_restore_command, shell=True, env={'PGPASWORD': passwd})

        command.wait()

    except CalledProcessError as e:
        
        success = False
        print(e)


    return success

def main():

    credentials = get_remote_db_credentials()
    user = credentials['user']
    database = credentials['db']
    address = credentials['address']
    password = credentials['password']

    dump_file = 'sapiencia'
    print(credentials)
    # print('Restaurando dump em na nova instancia')
    do_pg_restore(address, user, password, database, dump_file)


if __name__ == "__main__":
    main()