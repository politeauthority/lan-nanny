"""Scan Alerts

"""
from datetime import timedelta
import logging

import arrow
import slack

from ..collections.scan_hosts import ScanHosts
from ..collections.alerts import Alerts as CollectAlerts
from ..collections.devices import Devices
from ..collections.device_witnesses import DeviceWitnesses
from ..models.alert import Alert
from ..models.entity_meta import EntityMeta
from ..models.database_growth import DatabaseGrowth


class ScanAlerts:

    def __init__(self, scan):
        self.conn = scan.conn
        self.cursor = scan.cursor
        self.options = scan.options
        self.hosts = scan.hosts
        self.host_scan_log = scan.scan_hosts_log
        self.devices = {}
        self.new_devices = scan.new_devices
        self.trigger = scan.trigger
        self.new_alerts = []
        self.resolved_alerts = []
        self.device_collect = Devices(self.conn, self.cursor)
        self.device_witness_collect = DeviceWitnesses(self.conn, self.cursor)

    def run(self):
        """Handle various LanNanny alerts."""
        logging.info('Running alerts')
        # if self.trigger  != 'manual':
        #     logging.warning('Not running alerts via cron.')
        #     return True

        if not self.options['alerts-enabled'].value:
            logging.info('\tAlerts are Disabled')
            return True

        self.get_active_alerts()
        self.alert_no_hosts_in_scan()
        self.alert_new_device()
        self.alert_device_offline()
        self.alert_device_online()
        self.notify()

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
        # TODO: REWORK TO GRAB devices.new_devices and check for existing alerts
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
            self.new_alerts.append(alert_new)

            logging.info("\tCreated new device alert for %s" % new_device)

    def _validate_run_new_device_alert(self) -> bool:
        """Run checks to see if the new device alert should run.
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
        if (
            not first_growth
            or first_growth.created_ts > arrow.utcnow().datetime - timedelta(hours=1)
        ):
            logging.info('\tNot running new device alert, system is too new.')
            return True

        return True

    def alert_device_offline(self) -> bool:
        """Manage alerts for devices offline."""
        logging.info('\tRunning Device offline alerts')

        self.handle_offline_alerts()
        self.handle_offline_alerts_resolved()
        return True

    def alert_device_online(self) -> bool:
        print('online')
        # if self.trigger  != 'manual':
        #     logging.warning('Not running alerts via cron.')
        #     return True
        logging.info('\tRunning Device online alerts')

        devices_online = self.get_devices_w_online_alerts_triggered()
        if not devices_online:
            logging.info('\t\tNo new device online alerts found.')
            return True

        created_alerts = 0
        for device in devices_online:
            active_alert = self.device_alert_active(device, 'device-online')
            if not active_alert:
                logging.debug('\t%s is online, creating a new online alert.' % device)
                alert = Alert(self.conn, self.cursor)
                alert.kind = 'device-online'
                alert.active = True
                alert.last_observed_ts = arrow.utcnow().datetime
                alert.meta_update('device', device.id, 'int')
                created_alerts += 1
                self.new_alerts.append(alert)
            else:
                logging.debug('\t%s is online and has an active alert.' % device)
                alert = active_alert
                alert.last_observed_ts = arrow.utcnow().datetime
            alert.save()
        logging.debug('Created %s new online alerts' % created_alerts)

    def handle_offline_alerts(self):
        """
        """
        devices_offline = self.get_devices_w_offline_alerts_triggered()
        created_offline_alerts = 0
        # For each offline device with an offline alerts enable, create or update the alert.
        for device in devices_offline:
            active_alert = self.device_alert_active(device, 'device-offline')
            if not active_alert:
                logging.debug('\t%s is offline, creating a new offline alert.' % device)
                alert = Alert(self.conn, self.cursor)
                alert.kind = 'device-offline'
                alert.active = True
                alert.last_observed_ts = arrow.utcnow().datetime
                alert.meta_update('device', device.id, 'int')
                created_offline_alerts += 1
                self.new_alerts.append(alert)
            else:
                logging.debug('\t%s is offline and has an active alert.' % device)
                alert = active_alert
                alert.last_observed_ts = arrow.utcnow().datetime
            alert.save()

        logging.debug('Created %s new offline alerts' % created_offline_alerts)

    def get_devices_w_offline_alerts_triggered(self) -> list:
        """Get devices with offline alerts enabled, that are offline."""
        device_collect = Devices(self.conn, self.cursor)
        devices_w_alert = device_collect.get_with_meta_value('alert_offline', 1)
        logging.debug('\t\tFound %s devices with offline alerts enabled.' % len(devices_w_alert))

        default_jitter_timeout = arrow.utcnow().datetime - \
            timedelta(minutes=int(self.options["active-timeout"].value))

        # Run through devices with offline alerts.
        devices_offline_to_alert = []
        for device in devices_w_alert:
            # If device has custom alert jitter use it,
            custom_device_jitter = device.get_alert_jitter()
            if custom_device_jitter:
                jitter_timeout = arrow.utcnow().datetime - \
                    timedelta(minutes=int(custom_device_jitter))
                logging.debug('DEVICE HAS CUSTOM JITTER %s' % jitter_timeout)
            else:
                jitter_timeout = default_jitter_timeout
            # If device was last seen within the active timeout range, skip it.
            if device.last_seen > jitter_timeout:
                logging.debug('\tDevice %s was seen recently, not alerting.' % device)
                continue
            logging.debug('\tDevice %s is offline' % device)
            devices_offline_to_alert.append(device)
            self.devices[device.id] = device

        return devices_offline_to_alert

    def device_alert_active(self, device, alert_type):
        """Check if device has an active offline alert already set and return it if it does,
           otherwise return False.
        """
        for alert in self.active_alerts:
            if alert.kind != alert_type:
                continue
            if device.id == int(alert.metas['device'].value):
                return alert
        return False

    def device_alert_on_off_active(self, device, alert_type):
        """Check if device has an active offline alert already set and return it if it does,
           otherwise return False.
        """
        for alert in self.active_alerts:
            if alert.kind != alert_type:
                continue
            if device.id == int(alert.metas['device'].value):
                return alert
        return False

    def handle_offline_alerts_resolved(self):
        """
        """
        # Get all active device-offline alerts
        offline_alerts = []
        for alert in self.active_alerts:
            if alert.kind != 'device-offline':
                continue
            offline_alerts.append(alert)

        # Check to see if any active offline alerts should be turned off because the device is back
        # online

        device_alerts_to_resolve = []
        for alert in offline_alerts:
            alert_device_id = int(alert.metas['device'].value)
            for host in self.hosts:
                host_id = host['device'].id
                if alert_device_id == host_id:
                    logging.debug('\tDevice %s is back online.' % host['device'])
                    device_alerts_to_resolve.append(alert)
                    self.devices[host_id] = host['device']
                    break

        if not device_alerts_to_resolve:
            return True

        logging.info('\tFound %s device offline alerts to resolve.' % len(device_alerts_to_resolve))
        for alert in device_alerts_to_resolve:
            alert.resolved_ts = arrow.utcnow().datetime
            alert.active = False
            alert.save()
            logging.info('Resolved offline device alert for device id: %s' %
                         alert.metas['device'].value)
            self.resolved_alerts.append(alert)
        return True

    def get_devices_w_online_alerts_triggered(self):
        devices_w_alert = self.device_collect.get_with_meta_value('alert_online', 1)
        logging.debug('Found %s devices with online alerts enabled.' % len(devices_w_alert))

        jitter_timein = arrow.utcnow().datetime - \
            timedelta(minutes=int(self.options["active-timeout"].value))

        devices_online_to_alert = []
        for device in devices_w_alert:

            device_online_now = False
            for host in self.hosts:
                if device.id == host['device'].id:
                    device_online_now = True
                    break
            if not device_online_now:
                continue
            witnesses = self.device_witness_collect.get_device_since(
                device.id,
                jitter_timein,
                except_scan_id=self.host_scan_log.id)
            if witnesses:
                continue
            devices_online_to_alert.append(device)
            self.devices[device.id] = device

        return devices_online_to_alert

    def notify(self):
        """ """

        if not self.new_alerts and not self.resolved_alerts:
            logging.debug('No new alerts or resolved alerts, not sending notifications.')
            return True

        if not self.options['notification-slack-enabled'].value:
            logging.debug('Slack notifications not enabled')
            return True

        msg = self.notify_new_alerts()
        msg += self.notify_resolved_alerts()

        self.send_slack(msg)

    def notify_new_alerts(self) -> str:
        msg = ""
        for alert in self.new_alerts:
            alert_device = None
            if 'device' in alert.metas:
                alert_device = self.devices[int(alert.metas['device'].value)]
            if alert.kind == 'device-offline':
                msg += "Device %s is now offline.\n" % alert_device.name
            elif alert.kind == 'device-online':
                msg += "Device %s is online.\n" % alert_device.name
            else:
                msg += "There was an alert we don't know how to talk about yet.\n"
        return msg

    def notify_resolved_alerts(self) -> str:
        msg = ""
        for alert in self.resolved_alerts:
            alert_device = None
            if 'device' in alert.metas:
                alert_device = self.devices[int(alert.metas['device'].value)]
            if alert.kind == 'device-offline':
                msg += "Device %s is back online, resolving the alert.\n" % alert_device.name
            else:
                msg += "There was an alert resolved we dont know how to talk about yet.\n"
        return msg

    def send_slack(self, msg: str) -> bool:
        """Sends a slack message. """
        slack_token = self.options['notification-slack-token'].value
        if not slack_token:
            logging.error('No slack token found, cannot send notifications.')
            return False
        slack_channel = self.options['notification-slack-channel'].value
        if not slack_channel:
            logging.error('No slack channel found, cannot send notifications.')
            return False

        slack_client = slack.WebClient(token=slack_token)
        logging.info('Sending: %s' % msg)
        slack_client.chat_postMessage(
            username='Lan Nanny',
            channel=slack_channel,
            text=msg
        )
        return True

# End File: lan-nanny/lan_nanny/modules/scanning/scan_alerts.py
