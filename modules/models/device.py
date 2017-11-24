
"""


"""
import sys
sys.path.append('../,,./')
import conf


class Device(object):

    def get_all(self, db):
        """
        Grabs all devices that are known from the lan_nanny.devices table.

        :param db: The database connection object,
        :type: db: obj
        :return: All the devides that have ever been seen by Lan Nanny.
        :rtype: dict
        """
        d = {}
        sql = """
            SELECT *
            FROM `lan_nanny`.`devices`; """
        known_devices = db.ex(sql)
        for kd in known_devices:
            d[kd[0]] = {
                'id': kd[0],
                'name': kd[1],
                'mac': kd[2],
                'last_seen': kd[3],
                'last_ip': kd[4],
                'person_id': kd[6]
            }
        return d

    def save(self, device, db):
        """
        Inserts a row into the devices table.

        :param device: The info from the Nmap scan regaurding the device.
        :type: device: dict
        :param db: The database connection object,
        :type: db: obj
        :return: The new id of the device. (device_id)
        :rtype: int
        """
        self.__save_insert_qry(device, db)
        return self.__get_last_insert(db)

    def __save_insert_qry(self, device, db):
        """
        Writes a brand new insert based on criteria.

        :param device: The info from the Nmap scan regaurding the device.
        :type: device: dict
        :param db: The database connection object,
        :type: db: obj
        """
        vals = {
            # 'name': device['name'],
            'mac': device['mac'],
            'last_seen': device['scan_time'],
            'first_seen': device['scan_time'],
            'last_ip': device['current_ip'],
            'last_hostname': '',
            'seen_by': conf.machine_id,
        }
        qry = """
            INSERT INTO `lan_nanny`.`devices`
            (mac, last_seen, first_seen, last_ip, last_hostname, seen_by)
            VALUES (
                "%(mac)s",
                "%(last_seen)s",
                "%(last_seen)s",
                "%(last_ip)s",
                "%(last_hostname)s",
                "%(seen_by)s
                )
                ;"""
        qry = qry % vals
        db.ex(qry)

    def __get_last_insert(self, db):
        """
        Provides the last new device_id

        :param db: The database connection object,
        :type: db: obj
        :return: The last stored device_id
        :rtype: int
        """
        qry2 = """
            SELECT max(id)
            FROM `lan_nanny`.`devices`; """
        return db.ex(qry2)[0][0]

    def update_device(self, device, db):
        """
        Updates the devide db record.

        :param device: The info from the Nmap scan regaurding the device.
        :type: device: dict
        :param db: The database connection object,
        :type: db: obj
        """
        qry = """
            UPDATE `lan_nanny`.`devices`
            SET
                last_seen="%s",
                last_ip="%s",
                seen_by="%s"
             WHERE `mac`="%s"; """ % (
            device['scan_time'],
            device['current_ip'],
            conf.machine_id,
            device['mac'])
        db.ex(qry)

# End File: lan-nanny/modules/models/device.py
