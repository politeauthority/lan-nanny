"""Install
Creates the lan nanny db and tables, as well as populating options and their defaults.

"""
import subprocess

from modules import db
from config import default as config_default
conn, cursor = db.create_connection(config_default.LAN_NANNY_DB_FILE)


def run():
    """
    Main entry point to scanning script.

    """
    db.create_tables(conn, cursor)
    db.populate_options(conn, cursor)


def pip_requirements():
    """
    Installs pip requirements.

    """
    try:
        subprocess.check_output('pip3 install -r requirements.txt', shell=True)
    except subprocess.CalledProcessError:
        subprocess.check_output('pip install -r requirements.txt', shell=True)
    except subprocess.CalledProcessError:
        print('Error install pip requirements')
        exit(1)


def sys_requrirements():
    """
    Check and install system required software.
    @note this is pseudo code

    """
    x = subprocess.check_output('which nmap', shell=True)
    if not x:
        subprocess.check_output('apt-get install -y nmap', shell=True)


if __name__ == '__main__':
    run()

# End File: lan-nanny/lan_nanny/install-upgrade.py
