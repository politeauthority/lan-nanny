"""Scan Alerts

"""
import arrow

from ..collections.scan_hosts import ScanHosts
from ..collections.alerts import Alerts as CollectAlerts
from ..models.alert import Alert


class Alerts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.hosts = scan.hosts


    def run(self):
        """Handle various LanNanny alerts."""
        print('Running alerts')
        self.get_active_alerts()
        self.check_no_hosts_in_scan()

    def get_active_alerts(self):
        alert_collect = CollectAlerts(self.conn, self.cursor)
        active = alert_collect.get_active()
        self.active_alerts = active

        self.active_no_hosts = None
        for alert in self.active_alerts:
            if alert.kind == 'no-hosts-over-time':
                self.active_no_hosts = alert

    def check_no_hosts_in_scan(self):
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
                print('Created no-hosts-over-time alert')

            else:
                host_scan_alert = self.active_no_hosts
                print('Alert no-hosts-over-time still active')

            host_scan_alert.last_observed_ts = arrow.utcnow().datetime
            host_scan_alert.message = "No hosts have been seen on network for at least 3 hours period"
            host_scan_alert.save()

        elif hosts and host_scan_alert:
            host_scan_alert.active = False
            host_scan_alert.resolved_ts = arrow.utcnow().datetime
            host_scan_alert.save()
            print('Resolved alert no-hosts-over-time')

        return True


# End File: lan-nanny/lan_nanny/modules/scanning/alerts.py
