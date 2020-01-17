-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ambiosensing_working_profile
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ambiosensing_working_profile
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ambiosensing_working_profile` DEFAULT CHARACTER SET utf8 ;
USE `ambiosensing_working_profile` ;

-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`profile`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`profile` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`profile` (
  `idprofile` INT NOT NULL AUTO_INCREMENT,
  `profile_name` VARCHAR(255) NULL,
  PRIMARY KEY (`idprofile`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`activation_strategy`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`activation_strategy` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`activation_strategy` (
  `id_activation_strategy` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL,
  `profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`id_activation_strategy`, `profile_idprofile`),
  INDEX `fk_activation_strategy_profile_idx` (`profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_activation_strategy_profile`
    FOREIGN KEY (`profile_idprofile`)
    REFERENCES `ambiosensing_working_profile`.`profile` (`idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`strategy_temporal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`strategy_temporal` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`strategy_temporal` (
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
  `strategy_temporalcol` VARCHAR(45) NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  `activation_strategy_profile_idprofile` INT NOT NULL,
  INDEX `fk_strategy_temporal_activation_strategy1_idx` (`activation_strategy_id_activation_strategy` ASC, `activation_strategy_profile_idprofile` ASC) VISIBLE,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`, `activation_strategy_profile_idprofile`),
  CONSTRAINT `fk_strategy_temporal_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy` , `activation_strategy_profile_idprofile`)
    REFERENCES `ambiosensing_working_profile`.`activation_strategy` (`id_activation_strategy` , `profile_idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`strategy_volume`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`strategy_volume` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`strategy_volume` (
  `min` DECIMAL NULL,
  `max` DECIMAL NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  `activation_strategy_profile_idprofile` INT NOT NULL,
  INDEX `fk_strategy_volume_activation_strategy1_idx` (`activation_strategy_id_activation_strategy` ASC, `activation_strategy_profile_idprofile` ASC) VISIBLE,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`, `activation_strategy_profile_idprofile`),
  CONSTRAINT `fk_strategy_volume_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy` , `activation_strategy_profile_idprofile`)
    REFERENCES `ambiosensing_working_profile`.`activation_strategy` (`id_activation_strategy` , `profile_idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`strategy_alarm`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`strategy_alarm` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`strategy_alarm` (
  `name` VARCHAR(128) NOT NULL,
  `state` VARCHAR(45) NOT NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  `activation_strategy_profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`, `activation_strategy_profile_idprofile`),
  CONSTRAINT `fk_strategy_alarm_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy` , `activation_strategy_profile_idprofile`)
    REFERENCES `ambiosensing_working_profile`.`activation_strategy` (`id_activation_strategy` , `profile_idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`equipment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`equipment` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`equipment` (
  `id_equipment` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `type` VARCHAR(128) NULL,
  `equipmentcol` VARCHAR(45) NULL,
  PRIMARY KEY (`id_equipment`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_working_profile`.`schedule`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_working_profile`.`schedule` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_working_profile`.`schedule` (
  `id_schedule` INT NOT NULL AUTO_INCREMENT,
  `start` DATETIME NULL,
  `endl` DATETIME NULL,
  `profile_idprofile` INT NOT NULL,
  `equipment_id_equipment` INT NOT NULL,
  PRIMARY KEY (`id_schedule`, `profile_idprofile`, `equipment_id_equipment`),
  INDEX `fk_schedule_profile1_idx` (`profile_idprofile` ASC) VISIBLE,
  INDEX `fk_schedule_equipment1_idx` (`equipment_id_equipment` ASC) VISIBLE,
  CONSTRAINT `fk_schedule_profile1`
    FOREIGN KEY (`profile_idprofile`)
    REFERENCES `ambiosensing_working_profile`.`profile` (`idprofile`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_schedule_equipment1`
    FOREIGN KEY (`equipment_id_equipment`)
    REFERENCES `ambiosensing_working_profile`.`equipment` (`id_equipment`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
