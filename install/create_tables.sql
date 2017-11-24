CREATE TABLE `lan_nanny`.`devices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `mac` varchar(17) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_hostname` varchar(255) DEFAULT NULL,
  `people_id` int(10) DEFAULT NULL,
  `seen_by` varchar(50) DEFAULT NULL,
  `first_seen` datetime DEFAULT NULL,
  `meta` text,
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `lan_nanny`.`witness` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `device_id` int(10) NOT NULL,
  `date` datetime DEFAULT NULL,
  `seen_by` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 |
+---------+--------------------------------------------------