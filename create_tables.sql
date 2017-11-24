CREATE TABLE `phinder`.`devices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `mac` varchar(17) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_hostname` varchar(255) DEFAULT NULL,
  `people_id` int(10) DEFAULT NULL,
  `seen_by` varchar(50) default NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mac` (`mac`)
) ENGINE=InnoDB;

CREATE TABLE `phinder`.`people` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_device_id` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE `phinder`.`people` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_ip` varchar(15) DEFAULT NULL,
  `last_device_id` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;