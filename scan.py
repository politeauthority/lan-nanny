"""Scan

"""
from datetime import datetime
import subprocess

import arrow
from modules import parse_nmap
from modules import db
from modules.device import Device

NMAP_SCAN_FILE = "tmp.xml"
NMAP_SCAN_RANGE = "1-255"
NMAP_DB = "lan_nanny.db"

conn, cursor = db.create_connection(NMAP_DB)


def run():
    """
    Main entry point to scanning script.

    """
    hosts = scan()

    handle_devices(hosts)

def scan() -> dict:
    """
    Runs NMap scan.

    """
    print('Running scan')

    cmd = "nmap -sP 192.168.1.%s -oX %s" % (NMAP_SCAN_RANGE, NMAP_SCAN_FILE)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        print('Error running scan, please try again')
        exit(1)
    hosts = parse_nmap.parse_hosts(NMAP_SCAN_FILE)

    return hosts


def handle_devices(hosts):
    """
    Handles devices found in NMap scan, creating records for new devices, updating last seen for
    already known devices and saving witness for all found devices.

    """
    print('Found %s devices:' % len(hosts))

    scan_time = arrow.utcnow().datetime
    for host in hosts:
        device = Device(conn, cursor).get_by_mac(host['mac'])
        new = False
        if not device.mac:
            new = True
            device = device.create(scan_time, host)
        else:
            device.last_seen = scan_time
            device.update()

        new_device_str = ""
        if new:
            new_device_str = "\t- New Device"
        if device.name:
            print('\t%s - %s%s' % (device.name, device.ip, new_device_str))
        elif device.vendor:
            print('\t%s - %s%s' % (device.vendor, device.ip, new_device_str))
        else:
            print('\t%s - %s%s' % (device.mac, device.ip, new_device_str))

        _save_witness(device, scan_time)


def _save_witness(device: Device, scan_time: datetime) -> int:
    """
    Creates a record in the `witness` table of the devices id and scan time.

    """
    sql = """
        INSERT INTO witness
        (device_id, witness_ts)
        VALUES (?, ?)"""
    
    witness = (
        device.id,
        scan_time)

    cursor.execute(sql, witness)
    conn.commit()
    return cursor.lastrowid

if __name__ == '__main__':
    run()

# End File: lan-nanny/scan.py