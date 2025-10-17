-- SCHEMA
CREATE DATABASE IF NOT EXISTS photosite;

USE photosite;

-- DROP (để chạy lại an toàn)
DROP TABLE IF EXISTS PurchaseImage;
DROP TABLE IF EXISTS ImageCategory;
DROP TABLE IF EXISTS CartImage;
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS Image;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Vendor;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS User;


-- CORE ENTITIES
CREATE TABLE User (
  userID   CHAR(36)     NOT NULL,
  username  VARCHAR(50)  NOT NULL UNIQUE,
  password  VARCHAR(255) NOT NULL,
  email     VARCHAR(100),
  firstname VARCHAR(100),
  surname   VARCHAR(100),
  phone     VARCHAR(20),
  role		ENUM('Admin', 'Customer') DEFAULT 'Customer',
  customerRank ENUM('Bronze', 'Silver', 'Gold'),
  bio          TEXT,
  portfolio VARCHAR(400),
  PRIMARY KEY (userID)
);


CREATE TABLE Category (
  categoryID   CHAR(36)     NOT NULL,
  categoryName VARCHAR(50)  NOT NULL UNIQUE,
  description  TEXT,
  PRIMARY KEY (categoryID)
);

-- IMAGE / PURCHASE
CREATE TABLE Image (
  imageID     CHAR(36)     NOT NULL,
  userID    CHAR(36)     NOT NULL,
  title       VARCHAR(100) NOT NULL,
  description TEXT,
  price       DECIMAL(12,2) NOT NULL, 
  currency ENUM('USD', 'EUR', 'AUD') DEFAULT 'USD',
  updateDate  DATE,
  imageStatus ENUM('Active', 'Draft') DEFAULT 'ACTIVE',
  quantity    INT DEFAULT 0,
  extension   VARCHAR(10),
  PRIMARY KEY (imageID),
  CONSTRAINT fk_img_vendor
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Purchase (
  purchaseID   CHAR(36)     NOT NULL,
  userID   CHAR(36)     NOT NULL,
  currency ENUM('USD', 'EUR', 'AUD') DEFAULT 'USD',
  purchaseDate DATE,
  totalAmount  DECIMAL(12,2) NOT NULL, 
  PRIMARY KEY (purchaseID),
  CONSTRAINT fk_purchase_customer
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);


CREATE TABLE ImageCategory (
  categoryID CHAR(36) NOT NULL,
  imageID    CHAR(36) NOT NULL,
  PRIMARY KEY (categoryID, imageID),
  CONSTRAINT fk_ic_category
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ic_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CartImage (
  userID CHAR(36) NOT NULL,
  imageID    CHAR(36) NOT NULL,
  PRIMARY KEY (userID, imageID),
  CONSTRAINT fk_cart_customer
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_cart_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE PurchaseImage (
  purchaseID CHAR(36) NOT NULL,
  imageID    CHAR(36) NOT NULL,
  PRIMARY KEY (purchaseID, imageID),
  CONSTRAINT fk_pi_purchase
    FOREIGN KEY (purchaseID) REFERENCES Purchase(purchaseID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_pi_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Rating (
  ratingID   CHAR(36) NOT NULL,
  userID CHAR(36) NOT NULL,
  imageID    CHAR(36) NOT NULL,
  score      INT    NOT NULL,        
  comment    TEXT,
  updateDate DATE,
  PRIMARY KEY (ratingID),
  UNIQUE KEY uq_rating_once (userID, imageID),
  CONSTRAINT chk_score_range CHECK (score >= 0.0 AND score <= 5.0),
  CONSTRAINT fk_rating_customer
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_rating_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);
