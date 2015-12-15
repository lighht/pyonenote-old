import os
import sys

from clint.textui import colored

from pyonenote import mkdir, CONFIG_DIR
from pyonenote.api import client

try:
    if not os.path.exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)
        print(colored.green('Created path "' + CONFIG_DIR + '".'))
except Exception as e:
    print(colored.red('Fatal error: ' + str(e)))
    sys.exit(1)


def add_account():
    client_obj = client.Client()
    print(client_obj.get_auth_uri())
    url = input('Paste the link:')
    session_info = client_obj.get_session_info(uri=url)
    print(session_info['expires_at'])
    client_obj.dump()


def main():
    add_account()


if __name__ == '__main__':
    main()
