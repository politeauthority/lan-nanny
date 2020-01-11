"""Alerts

"""
# import os
# import subprocess

# import arrow

# from ..collections.devices import Devices
# from ..models.port import Port
# from . import parse_nmap


class Alerts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.tmp_dir = scan.tmp_dir
        self.scan_file = os.path.join(self.tmp_dir, 'host-scan.xml')
        self.hosts = scan.hosts

    def run(self, hosts: list):
        """
        Handles alerts for devices online or offline.

        """
        print('Running alerts')
        device_collection = Devices(conn, cursor)
        devices = device_collection.with_alerts_on()
        witness = Witness(conn, cursor)

        for device in devices:

            # Device offline check
            if device.alert_offline:
                device_alert = Alert(conn, cursor)
                device_active_offline_alert = device_alert.get_active(device.id, 'offline')
                #  If the device is not in the most recent scan, register the alert.
                device_in_scan = witness.get_device_for_scan(device.id, self.scan_log.id)
                if not device_in_scan:
                    device_offline_seconds = (arrow.utcnow().datetime - device.last_seen).seconds
                    timeout_seconds = int(self.options['active-timeout'].value) * 60

                    # if the device has been offline longer than the active time out, alert.
                    if device_offline_seconds > timeout_seconds:
                        self.create_alert(device, 'offline')
                    else:
                        time_til_alert = timeout_seconds - device_offline_seconds
                        msg = """Device %s is offline, but has not passed active time out """ \
                            + """ yet, %s seconds until alert.""" % device, time_til_alert
                        print(msg)

                # If the device has an active alert and IS online, we need to set the alert inactive
                else:
                    self.deactivate_alert(device_alert)

            # Device online check
            if device.alert_online == 1:
                device_online = False
                for host in hosts:
                    if device.mac == host['mac']:
                        device_online = True
                        break

                if not device_online:
                    continue

    def create_alert(self, device: Device, alert_type: str):
        """
        Creates an alert unless there's a current active alert for the device and alert type.

        """
        alert = Alert(conn, cursor)
        active_device_alert = alert.get_active(device.id, alert_type)
        if active_device_alert:
            print('Device %s already has an active %s alert.' % (device.name, alert_type))
            self.maintain_active_alert(alert)
            return

        alert.device_id = device.id
        alert.alert_type = alert_type
        alert.acked = 0
        alert.active = 1
        alert.save()

        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'created'
        alert_event.save()

        print('Created %s alert for %s' % (alert_type, device.name))
        self.new_alerts.append(alert)

    def maintain_active_alert(self, alert: Alert):
        """
        """
        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'still_active'
        alert_event.save()

    def deactivate_alert(self, alert: Alert):
        """
        """
        alert.active = False
        alert.save()
        alert_event = AlertEvent(conn, cursor)
        alert_event.alert_id = alert.id
        alert_event.event_type = 'deactivate'
        alert_event.save()


# End File: lan_nanny/nanny-nanny/modules/alerts.py
