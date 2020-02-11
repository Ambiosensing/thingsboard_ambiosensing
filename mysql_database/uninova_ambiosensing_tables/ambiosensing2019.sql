-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ambiosensing_BD
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `ambiosensing_BD` ;

-- -----------------------------------------------------
-- Schema ambiosensing_BD
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ambiosensing_BD` DEFAULT CHARACTER SET utf8 ;
USE `ambiosensing_BD` ;

-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`building`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`building` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`building` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`space`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`space` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`space` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL,
  `area` DECIMAL NULL,
  `ocupation_type` VARCHAR(45) NULL,
  `building_id` INT NOT NULL,
  PRIMARY KEY (`id`, `building_id`),
  INDEX `fk_space_building1_idx` (`building_id` ASC) VISIBLE,
  CONSTRAINT `fk_space_building1`
    FOREIGN KEY (`building_id`)
    REFERENCES `ambiosensing_BD`.`building` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`profile`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`profile` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`profile` (
  `idprofile` INT NOT NULL AUTO_INCREMENT,
  `profile_name` VARCHAR(255) NULL,
  `state` TINYINT NOT NULL DEFAULT 0,
  `space_id` INT NOT NULL,
  `space_building_id` INT NOT NULL,
  PRIMARY KEY (`idprofile`, `space_id`, `space_building_id`),
  INDEX `fk_profile_space1_idx` (`space_id` ASC, `space_building_id` ASC) VISIBLE,
  CONSTRAINT `fk_profile_space1`
    FOREIGN KEY (`space_id` , `space_building_id`)
    REFERENCES `ambiosensing_BD`.`space` (`id` , `building_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`activation_strategy`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`activation_strategy` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`activation_strategy` (
  `id_activation_strategy` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL,
  `profile_idprofile` INT NOT NULL,
  `profile_space_id` INT NOT NULL,
  `profile_space_building_id` INT NOT NULL,
  PRIMARY KEY (`id_activation_strategy`, `profile_idprofile`, `profile_space_id`, `profile_space_building_id`),
  INDEX `fk_activation_strategy_profile1_idx` (`profile_idprofile` ASC, `profile_space_id` ASC, `profile_space_building_id` ASC) VISIBLE,
  CONSTRAINT `fk_activation_strategy_profile1`
    FOREIGN KEY (`profile_idprofile` , `profile_space_id` , `profile_space_building_id`)
    REFERENCES `ambiosensing_BD`.`profile` (`idprofile` , `space_id` , `space_building_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`strategy_temporal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`strategy_temporal` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`strategy_temporal` (
  `monday` TINYINT NULL,
  `tuesday` TINYINT NULL,
  `wednesday` TINYINT NULL,
  `thursday` TINYINT NULL,
  `friday` TINYINT NULL,
  `saturday` TINYINT NULL,
  `sunday` TINYINT NULL,
  `spring` TINYINT NULL,
  `summer` TINYINT NULL,
  `autumn` TINYINT NULL,
  `winter` TINYINT NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`),
  CONSTRAINT `fk_strategy_temporal_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy`)
    REFERENCES `ambiosensing_BD`.`activation_strategy` (`id_activation_strategy`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`strategy_occupation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`strategy_occupation` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`strategy_occupation` (
  `min` DECIMAL NULL,
  `max` DECIMAL NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`),
  CONSTRAINT `fk_strategy_occupation_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy`)
    REFERENCES `ambiosensing_BD`.`activation_strategy` (`id_activation_strategy`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`device`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`device` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`device` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `type` VARCHAR(128) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`schedule`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`schedule` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`schedule` (
  `id_schedule` INT NOT NULL AUTO_INCREMENT,
  `start` DATETIME NULL,
  `endl` DATETIME NULL,
  `profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`id_schedule`, `profile_idprofile`),
  INDEX `fk_schedule_profile1_idx` (`profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_schedule_profile1`
    FOREIGN KEY (`profile_idprofile`)
    REFERENCES `ambiosensing_BD`.`profile` (`idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`device_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`device_configuration` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`device_configuration` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `state` TINYINT NULL,
  `operation_value` DECIMAL NULL,
  `device_id` INT NOT NULL,
  `schedule_id_schedule` INT NOT NULL,
  `schedule_profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`id`, `device_id`, `schedule_id_schedule`, `schedule_profile_idprofile`),
  INDEX `fk_device_configuration_device1_idx` (`device_id` ASC) VISIBLE,
  INDEX `fk_device_configuration_schedule1_idx` (`schedule_id_schedule` ASC, `schedule_profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_device_configuration_device1`
    FOREIGN KEY (`device_id`)
    REFERENCES `ambiosensing_BD`.`device` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_device_configuration_schedule1`
    FOREIGN KEY (`schedule_id_schedule` , `schedule_profile_idprofile`)
    REFERENCES `ambiosensing_BD`.`schedule` (`id_schedule` , `profile_idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`environmental_variables`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`environmental_variables` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`environmental_variables` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `value` DECIMAL NULL,
  `unit_type` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_BD`.`env_variable_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_BD`.`env_variable_configuration` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_BD`.`env_variable_configuration` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `min` DECIMAL NULL,
  `max` DECIMAL NULL,
  `environmental_variables_id` INT NOT NULL,
  `schedule_id_schedule` INT NOT NULL,
  `schedule_profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`id`, `environmental_variables_id`, `schedule_id_schedule`, `schedule_profile_idprofile`),
  INDEX `fk_env_variable_configuration_environmental_variables1_idx` (`environmental_variables_id` ASC) VISIBLE,
  INDEX `fk_env_variable_configuration_schedule1_idx` (`schedule_id_schedule` ASC, `schedule_profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_env_variable_configuration_environmental_variables1`
    FOREIGN KEY (`environmental_variables_id`)
    REFERENCES `ambiosensing_BD`.`environmental_variables` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_env_variable_configuration_schedule1`
    FOREIGN KEY (`schedule_id_schedule` , `schedule_profile_idprofile`)
    REFERENCES `ambiosensing_BD`.`schedule` (`id_schedule` , `profile_idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
