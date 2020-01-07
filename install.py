"""Install
Creates the lan nanny db and tables, as well as populating options and their defaults.

"""
import subprocess

from .modules import db

NMAP_DB = "galapago.db"

conn, cursor = db.create_connection(NMAP_DB)


def run():
    """
    Main entry point to scanning script.

    """
    db.populate_options(conn, cursor)

    db.create_tables(conn, cursor)


def pip_requiredments():
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


if __name__ == '__main__':
    run()

# End File: lan-nanny/install.py
