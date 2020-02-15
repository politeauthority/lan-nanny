"""Install
Creates the lan nanny db and tables, as well as populating options and their defaults.

"""
import os
import subprocess

from modules import db
from config import default as config_default
# conn, cursor = db.create_connection(config_default.LAN_NANNY_DB_FILE)


def run():
    """
    Main entry point to scanning script.

    """
    create_lan_nanny_space()
    install_lan_nanny_python()
    pip_requirements()
    conn, cursor = create_database()
    db.create_tables(conn, cursor)
    console_password = db.populate_options(conn, cursor)
    if console_password:
        print('Console password: %s' % console_password)

def create_lan_nanny_space():
    """Create the lan nanny install space"""
    linux_install_path = "/opt/lan-nanny"

    if not os.path.exists(linux_install_path):
        os.mkdir(linux_install_path)
    return True


def create_database():
    """Create the Lan Nanny DB, or establish connection, maybe both?"""
    conn, cursor = db.create_connection(config_default.LAN_NANNY_DB_FILE)
    return conn, cursor


def install_lan_nanny_python():
    """Run the python build/install process for lan nanny"""
    setup_path = os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 
            '../',
            'setup.py'))
    subprocess.Popen(['python3', setup_path, 'build'], True)
    subprocess.Popen(['sudo', 'python3', setup_path, 'install'], True)
    return True


def pip_requirements():
    """
    Installs pip requirements.

    """
    requirements_path = os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 
            '../',
            'requirements.txt'))
    try:
        subprocess.check_output('pip3 install -r %s' % requirements_path, shell=True)
    except subprocess.CalledProcessError:
        subprocess.check_output('pip install -r %s.txt' % requirements_path, shell=True)
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
