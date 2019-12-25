"""Scan

"""
from datetime import datetime
import subprocess

from modules import parse_nmap
from modules import db

NMAP_SCAN_FILE = "tmp.xml"
NMAP_SCAN_RANGE = "1-5"
NMAP_DB = "lan_nanny.db"

conn, cursor = db.create_connection(NMAP_DB)


def run():
    """
    Main entry point to scanning script.

    """
    hosts = scan()

    handle_devices(hosts)

def scan() -> dict:
    # cmd = "nmap -sP 192.168.1.1-255"
    cmd = "nmap -sP 192.168.1.%s -oX %s" % (NMAP_SCAN_RANGE, NMAP_SCAN_FILE)
    print('Running scan')
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        print('Error running scan, please try again')
        exit(1)
    hosts = parse_nmap.parse_hosts(NMAP_SCAN_FILE)
    print('Found %s hosts' % len(hosts))

    return hosts


def handle_devices(hosts):

    scan_time = datetime.now()
    for host in hosts:
        device = _get_device_by_mac(host['mac'])
        if not device:
            device_id = _create_device(host,  scan_time)
            device = _get_device_by_id(device_id)
            if device['vendor']:
                print('New Device:\t%s - %s' % (device['vendor'], device['ip']))
            else:
                print('New Device:\t%s' % (device['ip']))
        else:
            # device['id'] = device_id
            print(device)
            _update_device(device, scan_time)
        _save_witness(device, scan_time)


def _get_device_by_mac(mac: str) -> dict:
    """
    Gets a device from the devices table based on mac address.

    """
    sql = """SELECT * FROM devices WHERE mac='%s'""" % mac
    cursor.execute(sql)
    device_raw = cursor.fetchone()
    if not device_raw:
        return {}
    
    device = {
        'id': device_raw[0],
        'mac': device_raw[1],
        'vendor': device_raw[2],
        'ip': device_raw[3],
        'last_seen': device_raw[4],
        'first_seen': device_raw[5],
        'name': device_raw[6],
    }

    return device

def _get_device_by_id(device_id: int) -> dict:
    """
    Gets a device from the devices table based on it's device ID.

    """
    sql = """SELECT * FROM devices WHERE id=%s""" % device_id
    curor.execute(sql)
    device_raw = cursor.fetchone()
    if not device_raw:
        return {}
    
    device = {
        'id': device_raw[0],
        'mac': device_raw[1],
        'vendor': device_raw[2],
        'ip': device_raw[3],
        'last_seen': device_raw[4],
        'first_seen': device_raw[5],
        'name': device_raw[6],
    }

    return device

def _create_device(device: dict, scan_time: datetime) -> int:
    """
    Creates a device by inserting into the devices table, returning its new key.

    """
    sql = """
        INSERT INTO devices
        (mac, vendor, last_ip, last_seen, first_seen)
        VALUES (?, ?, ?, ?, ?)"""
    
    device = (
        device['mac'],
        device['vendor'],
        device['ip'],
        scan_time,
        scan_time)

    cursor.execute(sql, device)
    conn.commit()
    return cursor.lastrowid

def _update_device(device: dict, scan_time: datetime) -> bool:
    """
    Updates a device in the `devices` table setting its new last seen time to the scan time.

    """
    sql = """
        UPDATE devices
        SET last_seen = ?
        WHERE id = ?"""
    cursor.execute(sql, (scan_time, device['id']))
    conn.commit()
    return True

def _save_witness(device: dict, scan_time: datetime) -> int:
    """
    Creates a record in the `witness` table of the devices id and scan time.

    """
    sql = """
        INSERT INTO witness
        (device_id, witness_ts)
        VALUES (?, ?)"""
    
    witness = (
        device['id'],
        scan_time)

    cursor.execute(sql, witness)
    conn.commit()
    return cursor.lastrowid

if __name__ == '__main__':
    run()
