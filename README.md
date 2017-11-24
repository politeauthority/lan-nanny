# LAN Nanny
A tool for collecting and storing network devices by mac/ip and tagging the devices with custom naming.

##Example Usage
This will scan the entire range of ips given. When running regular scans, its best to target the expect DCHP ranges, if you're interested in units coming on and dropping off network.
```
sudo python lan_nanny.py --ip=192.168.1.1-255
```

## Install
You'll need the utility NMAP and the python-mysql connector

### MySQL Create Tables
```
CREATE TABLE `lan_nanny`.`devices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `mac` varchar(17) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_hostname` varchar(255) DEFAULT NULL,
  `people_id` int(10) DEFAULT NULL,
  `seen_by` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mac` (`mac`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lan_nanny`.`people` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_device_id` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1

 CREATE TABLE `lan_nanny`.`witness` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `device_id` int(10) NOT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=106517 DEFAULT CHARSET=latin1
```