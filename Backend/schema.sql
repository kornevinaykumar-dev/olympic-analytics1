CREATE DATABASE IF NOT EXISTS olympic_analytics_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE olympic_analytics_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  last_login DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS countries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  country_name VARCHAR(120) NOT NULL UNIQUE,
  noc_code VARCHAR(8) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sport_name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS olympics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  year INT NOT NULL,
  season VARCHAR(20) NOT NULL,
  city VARCHAR(120) NOT NULL,
  UNIQUE KEY uq_year_season (year, season)
);

CREATE TABLE IF NOT EXISTS medals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  olympic_id INT NOT NULL,
  country_id INT NOT NULL,
  sport_id INT NOT NULL,
  gold INT DEFAULT 0,
  silver INT DEFAULT 0,
  bronze INT DEFAULT 0,
  total INT DEFAULT 0,
  FOREIGN KEY (olympic_id) REFERENCES olympics(id),
  FOREIGN KEY (country_id) REFERENCES countries(id),
  FOREIGN KEY (sport_id) REFERENCES sports(id)
);

CREATE TABLE IF NOT EXISTS predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  country VARCHAR(120) NOT NULL,
  sport VARCHAR(120) NOT NULL,
  predicted_medal VARCHAR(20) NOT NULL,
  probability FLOAT NOT NULL,
  prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medals_olympic ON medals(olympic_id);
CREATE INDEX idx_medals_country ON medals(country_id);
CREATE INDEX idx_medals_sport ON medals(sport_id);
