"""Scan Alerts

"""
from datetime import timedelta
import logging

import arrow

from ..collections.scan_hosts import ScanHosts
from ..collections.alerts import Alerts as CollectAlerts
from ..collections.devices import Devices
from ..models.alert import Alert
from ..models.entity_meta import EntityMeta
from ..models.database_growth import DatabaseGrowth


class ScanAlerts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.hosts = scan.hosts
        self.new_devices = scan.new_devices
        self.trigger = scan.trigger

    def run(self):
        """Handle various LanNanny alerts."""
        logging.info('Running alerts')
        if not self.options['alerts-enabled'].value:
            logging.info('\tAlerts are Disabled')
            return True

        self.get_active_alerts()
        self.alert_no_hosts_in_scan()
        self.alert_new_device()
        self.alert_device_offline()

    def get_active_alerts(self):
        """Get all currently active alerts."""
        alert_collect = CollectAlerts(self.conn, self.cursor)
        active = alert_collect.get_firing()
        self.active_alerts = active

        self.active_no_hosts = None
        for alert in self.active_alerts:
            if alert.kind == 'no-hosts-over-time':
                self.active_no_hosts = alert

    def alert_no_hosts_in_scan(self) -> bool:
        """Create an alert if there's been no productive host scans in x seconds."""
        seconds_to_alert = 60 * 60 * 3  # 3 hours
        host_scans = ScanHosts(self.conn, self.cursor)
        scans_since = host_scans.get_since(seconds_to_alert)
        hosts = False
        for scan in scans_since:
            if scan.units and scan.units > 0:
                hosts = True
                break

        host_scan_alert = self.active_no_hosts
        if not hosts:
            if not self.active_no_hosts:
                host_scan_alert = Alert(self.conn, self.cursor)
                host_scan_alert.kind = 'no-hosts-over-time'
                host_scan_alert.active = True
                logging.info('Created no-hosts-over-time alert')

            else:
                host_scan_alert = self.active_no_hosts
                logging.info('Alert no-hosts-over-time still active')

            host_scan_alert.last_observed_ts = arrow.utcnow().datetime
            host_scan_alert.message = \
                "No hosts have been seen on network for at least 3 hours period"
            host_scan_alert.save()

        elif hosts and host_scan_alert:
            host_scan_alert.active = False
            host_scan_alert.resolved_ts = arrow.utcnow().datetime
            host_scan_alert.save()
            logging.info('Resolved alert no-hosts-over-time')

        return True

    def alert_new_device(self) -> bool:
        """Alert on new device discovery."""
        ## TODO: REWORK TO GRAB devices.new_devices and check for existing alerts
        # Run checks to see if new device alert should run.
        if not self._validate_run_new_device_alert():
            return False

        logging.info('\tRunning Alert on new devices, found %s' % len(self.new_devices))
        for new_device in self.new_devices:
            alert_new = Alert(self.conn, self.cursor)
            alert_new.kind = 'new-device'
            alert_new.active = True
            alert_new.last_observed_ts = arrow.utcnow().datetime
            alert_new.metas['device'] = EntityMeta(self.conn, self.cursor)
            alert_new.metas['device'].name = 'device'
            alert_new.metas['device'].type = 'str'
            alert_new.metas['device'].value = new_device.id
            alert_new.save()

            logging.info("\tCreated new device alert for %s" % new_device)

    def _validate_run_new_device_alert(self) -> bool:
        """
        Run checks to see if the new device alert should run.
        This alert should only run if all are True
            - The `alerts-new-device` setting is set True
            - Hosts were found in the last scan
            - New devices were found in the last scan
            - The Lan Nanny install is more than 1 hour old
        """
        if not self.options['alerts-new-device'].value:
            logging.info("\tNot running new device alert, because of alerts-new-device setting.")
            return False
        if not self.hosts:
            logging.info('\tNot running new device alert, no hosts found.')
            return False
        if not self.new_devices:
            logging.info('\tNot running new device alert, no new devices found.')
            return False

        # Don't run new device alerts if system is only 1 hour old.
        first_growth = DatabaseGrowth(self.conn, self.cursor)
        first_growth.get_by_id(1)
        if first_growth.created_ts > arrow.utcnow().datetime - timedelta(hours=1):
            logging.info('\tNot running new device alert, system is too new.')
            return True

        return True

    def alert_device_offline(self) -> bool:
        """Manage alerts for devices offline."""
        if self.trigger  != 'manual':
            return True

        logging.info('\tRunning Device offline alerts')
        devices_offline = self._get_devices_offline_w_alerting()

        for device in devices_offline:
            alert = Alert(self.conn, self.cursor)
            alert.kind = 'device-offline'
            alert.active = True
            alert.last_observed_ts = arrow.utcnow().datetime
            alert.meta_update('device', device.id, 'int')
            alert.save()
            print('saved alert')


        return True

    def _get_devices_offline_w_alerting(self) -> list:
        device_collect = Devices(self.conn, self.cursor)
        devices_w_alert = device_collect.get_with_meta_value('alert_offline', 'true')
        jitter_timeout = arrow.utcnow().datetime - \
            timedelta(minutes=int(self.options["active-timeout"].value))

        # Run through devices with offline alerts.
        devices_offline_to_alert = []
        for device in devices_w_alert:
            # If device was last seen within the active timeout range, skip it.
            if device.last_seen > jitter_timeout:
                continue
            for up_host in self.hosts:
                if up_host['device'].id == device.id:
                    break
            devices_offline_to_alert.append(device)
        return devices_offline_to_alert

            
# End File: lan-nanny/lan_nanny/modules/scanning/scan_alerts.py
