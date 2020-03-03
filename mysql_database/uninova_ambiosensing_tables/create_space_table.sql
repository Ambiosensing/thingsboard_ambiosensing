DELETE FROM `ambiosensing_bd`.`space`CREATE TABLE `space` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `area` decimal(10,0) DEFAULT NULL,
  `occupation_type` varchar(45) DEFAULT NULL,
  `id_thingsboard` varchar(255) DEFAULT NULL,
  `building_id` int NOT NULL,
  PRIMARY KEY (`id`,`building_id`),
  KEY `fk_space_building1_idx` (`building_id`),
  CONSTRAINT `fk_space_building1` FOREIGN KEY (`building_id`) REFERENCES `building` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
;
SELECT * FROM ambiosensing_bd.space;