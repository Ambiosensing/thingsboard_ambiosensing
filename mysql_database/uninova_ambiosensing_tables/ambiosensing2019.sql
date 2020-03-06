-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema ambiosensing_bd
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `ambiosensing_bd` ;

-- -----------------------------------------------------
-- Schema ambiosensing_bd
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ambiosensing_bd` DEFAULT CHARACTER SET utf8 ;
USE `ambiosensing_bd` ;

-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`building`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`building` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`building` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `id_thingsboard` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`space`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`space` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`space` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `area` DECIMAL(10,0) NULL DEFAULT NULL,
  `occupation_type` VARCHAR(45) NULL DEFAULT NULL,
  `id_thingsboard` VARCHAR(255) NULL DEFAULT NULL,
  `building_id` INT NOT NULL,
  PRIMARY KEY (`id`, `building_id`),
  INDEX `fk_space_building1_idx` (`building_id` ASC) VISIBLE,
  CONSTRAINT `fk_space_building1`
    FOREIGN KEY (`building_id`)
    REFERENCES `ambiosensing_bd`.`building` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`profile`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`profile` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`profile` (
  `idprofile` INT NOT NULL AUTO_INCREMENT,
  `profile_name` VARCHAR(255) NULL DEFAULT NULL,
  `state` TINYINT NOT NULL DEFAULT '0',
  `space_id` INT NOT NULL,
  PRIMARY KEY (`idprofile`, `space_id`),
  INDEX `fk_profile_space1_idx` (`space_id` ASC) VISIBLE,
  CONSTRAINT `fk_profile_space1`
    FOREIGN KEY (`space_id`)
    REFERENCES `ambiosensing_bd`.`space` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`activation_strategy`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`activation_strategy` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`activation_strategy` (
  `id_activation_strategy` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`id_activation_strategy`, `profile_idprofile`),
  INDEX `fk_activation_strategy_profile1_idx` (`profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_activation_strategy_profile1`
    FOREIGN KEY (`profile_idprofile`)
    REFERENCES `ambiosensing_bd`.`profile` (`idprofile`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`device`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`device` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`device` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL DEFAULT NULL,
  `type` VARCHAR(128) NULL DEFAULT NULL,
  `id_thingsboard` VARCHAR(255) NULL DEFAULT NULL,
  `space_id` INT NOT NULL,
  PRIMARY KEY (`id`, `space_id`),
  INDEX `fk_device_space1_idx` (`space_id` ASC) VISIBLE,
  CONSTRAINT `fk_device_space1`
    FOREIGN KEY (`space_id`)
    REFERENCES `ambiosensing_bd`.`space` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`schedule`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`schedule` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`schedule` (
  `idschedule` INT NOT NULL AUTO_INCREMENT,
  `start` DATETIME NULL DEFAULT NULL,
  `end` DATETIME NULL DEFAULT NULL,
  `profile_idprofile` INT NOT NULL,
  PRIMARY KEY (`idschedule`, `profile_idprofile`),
  INDEX `fk_schedule_profile1_idx` (`profile_idprofile` ASC) VISIBLE,
  CONSTRAINT `fk_schedule_profile1`
    FOREIGN KEY (`profile_idprofile`)
    REFERENCES `ambiosensing_bd`.`profile` (`idprofile`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`device_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`device_configuration` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`device_configuration` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `state` TINYINT NULL DEFAULT NULL,
  `operation_value` DECIMAL(10,0) NULL DEFAULT NULL,
  `device_id` INT NOT NULL,
  `schedule_idschedule` INT NOT NULL,
  PRIMARY KEY (`id`, `device_id`, `schedule_idschedule`),
  INDEX `fk_device_configuration_device1_idx` (`device_id` ASC) VISIBLE,
  INDEX `fk_device_configuration_schedule1_idx` (`schedule_idschedule` ASC) VISIBLE,
  CONSTRAINT `fk_device_configuration_device1`
    FOREIGN KEY (`device_id`)
    REFERENCES `ambiosensing_bd`.`device` (`id`),
  CONSTRAINT `fk_device_configuration_schedule1`
    FOREIGN KEY (`schedule_idschedule`)
    REFERENCES `ambiosensing_bd`.`schedule` (`idschedule`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`environmental_variables`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`environmental_variables` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`environmental_variables` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  `value` DECIMAL(10,0) NULL DEFAULT NULL,
  `unit_type` VARCHAR(45) NULL DEFAULT NULL,
  `space_id` INT NOT NULL,
  PRIMARY KEY (`id`, `space_id`),
  INDEX `fk_environmental_variables_space1_idx` (`space_id` ASC) VISIBLE,
  CONSTRAINT `fk_environmental_variables_space1`
    FOREIGN KEY (`space_id`)
    REFERENCES `ambiosensing_bd`.`space` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`env_variable_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`env_variable_configuration` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`env_variable_configuration` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `min` DECIMAL(10,0) NULL DEFAULT NULL,
  `max` DECIMAL(10,0) NULL DEFAULT NULL,
  `environmental_variables_id` INT NOT NULL,
  `schedule_idschedule` INT NOT NULL,
  PRIMARY KEY (`id`, `environmental_variables_id`, `schedule_idschedule`),
  INDEX `fk_env_variable_configuration_environmental_variables1_idx` (`environmental_variables_id` ASC) VISIBLE,
  INDEX `fk_env_variable_configuration_schedule1_idx` (`schedule_idschedule` ASC) VISIBLE,
  CONSTRAINT `fk_env_variable_configuration_environmental_variables1`
    FOREIGN KEY (`environmental_variables_id`)
    REFERENCES `ambiosensing_bd`.`environmental_variables` (`id`),
  CONSTRAINT `fk_env_variable_configuration_schedule1`
    FOREIGN KEY (`schedule_idschedule`)
    REFERENCES `ambiosensing_bd`.`schedule` (`idschedule`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`strategy_occupation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`strategy_occupation` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`strategy_occupation` (
  `min` DECIMAL(10,0) NULL DEFAULT NULL,
  `max` DECIMAL(10,0) NULL DEFAULT NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`),
  CONSTRAINT `fk_strategy_occupation_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy`)
    REFERENCES `ambiosensing_bd`.`activation_strategy` (`id_activation_strategy`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`strategy_temporal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`strategy_temporal` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`strategy_temporal` (
  `monday` TINYINT NULL DEFAULT NULL,
  `tuesday` TINYINT NULL DEFAULT NULL,
  `wednesday` TINYINT NULL DEFAULT NULL,
  `thursday` TINYINT NULL DEFAULT NULL,
  `friday` TINYINT NULL DEFAULT NULL,
  `saturday` TINYINT NULL DEFAULT NULL,
  `sunday` TINYINT NULL DEFAULT NULL,
  `spring` TINYINT NULL DEFAULT NULL,
  `summer` TINYINT NULL DEFAULT NULL,
  `autumn` TINYINT NULL DEFAULT NULL,
  `winter` TINYINT NULL DEFAULT NULL,
  `activation_strategy_id_activation_strategy` INT NOT NULL,
  PRIMARY KEY (`activation_strategy_id_activation_strategy`),
  CONSTRAINT `fk_strategy_temporal_activation_strategy1`
    FOREIGN KEY (`activation_strategy_id_activation_strategy`)
    REFERENCES `ambiosensing_bd`.`activation_strategy` (`id_activation_strategy`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_asset_devices`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_asset_devices` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_asset_devices` (
  `fromEntityType` VARCHAR(30) NULL DEFAULT NULL,
  `fromId` VARCHAR(100) NULL DEFAULT NULL,
  `fromName` VARCHAR(100) NULL DEFAULT NULL,
  `fromType` VARCHAR(100) NULL DEFAULT NULL,
  `toEntityType` VARCHAR(30) NULL DEFAULT NULL,
  `toId` VARCHAR(100) NULL DEFAULT NULL,
  `toName` VARCHAR(100) NULL DEFAULT NULL,
  `toType` VARCHAR(100) NULL DEFAULT NULL,
  `relationType` VARCHAR(50) NULL DEFAULT NULL,
  `relationGroup` VARCHAR(50) NULL DEFAULT NULL,
  `description` VARCHAR(999) NULL DEFAULT NULL,
  UNIQUE INDEX `thingsboard_asset_devices_pk` (`fromId` ASC, `toId` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'This is one of the several tables that the Ambiosensing project needs to keep up that do not reflect direct arrangements that are already made on the ThingsBoard installation side. This table establishes a more direct connection between\\nASSESTs and the DEVICEs that are associated/related to those assets. This relation is very important in our internal project structure but its not directly supported by the default ThingsBoard installation, i.e., there is not a direct API call\\nthat can return that per se.';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_authentication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_authentication` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_authentication` (
  `user_type` VARCHAR(30) NULL DEFAULT NULL,
  `token` VARCHAR(999) NULL DEFAULT NULL,
  `token_timestamp` DATETIME NULL DEFAULT NULL,
  `refreshToken` VARCHAR(999) NULL DEFAULT NULL,
  `refreshToken_timestamp` DATETIME NULL DEFAULT NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Table to store the authentication and refresh tokens for all the supported user types, namely \"SYS_ADMIN\", \"TENANT_ADMIN\" and \"CUSTOMER_USER\". This table is to be used as a place holder for these tokens so that its not needed to request\\nfor a new one every time a service is executed. This means that updated tokens should replace old, expired ones instead of writing a new one';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_customers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_customers` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_customers` (
  `entityType` VARCHAR(15) NULL DEFAULT NULL,
  `id` VARCHAR(100) NULL DEFAULT NULL,
  `createdTime` DATETIME NULL DEFAULT NULL,
  `description` VARCHAR(100) NULL DEFAULT NULL,
  `country` VARCHAR(70) NULL DEFAULT NULL,
  `state` VARCHAR(70) NULL DEFAULT NULL,
  `city` VARCHAR(70) NULL DEFAULT NULL,
  `address` VARCHAR(255) NULL DEFAULT NULL,
  `address2` VARCHAR(255) NULL DEFAULT NULL,
  `zip` VARCHAR(30) NULL DEFAULT NULL,
  `phone` VARCHAR(30) NULL DEFAULT NULL,
  `email` VARCHAR(30) NULL DEFAULT NULL,
  `title` VARCHAR(150) NULL DEFAULT NULL,
  `tenantId` VARCHAR(100) NULL DEFAULT NULL,
  `name` VARCHAR(100) NULL DEFAULT NULL,
  UNIQUE INDEX `thingsboard_customers_table_pk` (`id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Table to store the full information for a customer, as it is returned from the remote API.';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_devices`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_devices` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_devices` (
  `entityType` VARCHAR(15) NULL DEFAULT NULL,
  `name` VARCHAR(100) NULL DEFAULT NULL,
  `type` VARCHAR(100) NULL DEFAULT NULL,
  `timeseriesKeys` VARCHAR(999) NULL DEFAULT NULL,
  `id` VARCHAR(100) NULL DEFAULT NULL,
  `createdTime` DATETIME NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `tenantId` VARCHAR(100) NULL DEFAULT NULL,
  `customerId` VARCHAR(100) NULL DEFAULT NULL,
  UNIQUE INDEX `thingsboard_device_table_pk` (`id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Table to store the full information of a device, as well as all its relations (associated tenant and/or customer)';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_tenant_assets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_tenant_assets` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_tenant_assets` (
  `entityType` VARCHAR(15) NULL DEFAULT NULL,
  `id` VARCHAR(100) NULL DEFAULT NULL,
  `createdTime` DATETIME NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `tenantId` VARCHAR(100) NULL DEFAULT NULL,
  `customerId` VARCHAR(100) NULL DEFAULT NULL,
  `name` VARCHAR(100) NULL DEFAULT NULL,
  `type` VARCHAR(100) NULL DEFAULT NULL,
  UNIQUE INDEX `thingsboard_tenant_assets_table_pk` (`id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Table to store all assets belonging to a given tenant';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`tb_tenants`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`tb_tenants` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`tb_tenants` (
  `entityType` VARCHAR(15) NULL DEFAULT NULL,
  `id` VARCHAR(100) NULL DEFAULT NULL,
  `createdTime` DATETIME NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `country` VARCHAR(70) NULL DEFAULT NULL,
  `state` VARCHAR(70) NULL DEFAULT NULL,
  `city` VARCHAR(70) NULL DEFAULT NULL,
  `address` VARCHAR(255) NULL DEFAULT NULL,
  `address2` VARCHAR(255) NULL DEFAULT NULL,
  `zip` VARCHAR(30) NULL DEFAULT NULL,
  `phone` VARCHAR(30) NULL DEFAULT NULL,
  `email` VARCHAR(100) NULL DEFAULT NULL,
  `title` VARCHAR(150) NULL DEFAULT NULL,
  `region` VARCHAR(100) NULL DEFAULT NULL,
  `name` VARCHAR(100) NULL DEFAULT NULL,
  UNIQUE INDEX `thingsboard_tenants_table_pk` (`id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT = 'Table to store the full information for a tenant, as it is returned from the remote API';


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`device_hist`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`device_hist` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`device_hist` (
  `data` DATETIME NOT NULL,
  `id_thingsboard` VARCHAR(255) NOT NULL,
  `operation_state` TINYINT NOT NULL,
  `availability_state` TINYINT NOT NULL)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ambiosensing_bd`.`profile_hist`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ambiosensing_bd`.`profile_hist` ;

CREATE TABLE IF NOT EXISTS `ambiosensing_bd`.`profile_hist` (
  `data` DATETIME NOT NULL,
  `idprofile` INT NOT NULL,
  `state` TINYINT NOT NULL)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
