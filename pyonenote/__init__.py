__all__ = ['api', 'cli']
__author__ = "Dheepan"
__copyright__ = "Copyright © 2015-present Dheepan"
__created__ = "2015-12-08"
__credits__ = []
__email__ = "idheepan@outlook.com"
__license__ = "GPL 3.0"
__project__ = "pyonenote"
__status__ = "Development"
__updated__ = "2015-08-08"
__version__ = "0.0.0.dev"

import os
from pwd import getpwnam, getpwuid


def get_current_os_user():
    """
    Find the real user who runs the current process. Return a tuple of uid, username, homedir.
    :rtype: (int, str, str)
    """
    user_name = os.getenv('SUDO_USER')
    if not user_name:
        user_name = os.getenv('USER')
    if user_name:
        pw = getpwnam(user_name)
        user_uid = pw.pw_uid
    else:
        # If cannot find the user, use ruid instead.
        user_uid = os.getresuid()[0]
        pw = getpwuid(user_uid)
        user_name = pw.pw_name
    user_gid = pw.pw_gid
    user_home = pw.pw_dir
    return user_uid, user_name, user_home, user_gid


OS_USER_ID, OS_USER_NAME, OS_USER_HOME, OS_USER_GID = get_current_os_user()
OS_HOSTNAME = os.uname()[1]

CONFIG_DIR = OS_USER_HOME + '/.pyonenote'
SESSION_FILE = CONFIG_DIR + '/session.json'
NOTEBOOK_DB = CONFIG_DIR + '/notebook_db.pkl'
PAGE_DB = CONFIG_DIR + '/page_db.pkl'


def mkdir(path):
    os.makedirs(path, mode=0o700)
    os.chown(path, OS_USER_ID, OS_USER_GID)
