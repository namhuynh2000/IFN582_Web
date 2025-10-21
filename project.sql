-- SCHEMA
CREATE DATABASE IF NOT EXISTS photosite;
USE photosite;

-- DROP in dependency order (safe re-run)
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

-- ======================
-- CORE ENTITIES
-- ======================

CREATE TABLE User (
  userID    CHAR(36)     NOT NULL,
  username  VARCHAR(50)  NOT NULL UNIQUE,
  password  VARCHAR(255) NOT NULL,
  email     VARCHAR(100),
  firstname VARCHAR(100),
  surname   VARCHAR(100),
  phone     VARCHAR(20),
  role      ENUM('Admin','Customer','Vendor') NOT NULL DEFAULT 'Customer',
  isDeleted BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (userID)
);


CREATE TABLE Admin (
  userID CHAR(36) NOT NULL,
  PRIMARY KEY (userID),
  CONSTRAINT fk_admin_user
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Customer: subtype of User (PK = FK → User)
CREATE TABLE Customer (
  userID       CHAR(36) NOT NULL,
  customerRank ENUM('Bronze','Silver','Gold') NOT NULL DEFAULT 'Bronze',
  PRIMARY KEY (userID),
  CONSTRAINT fk_customer_user
    FOREIGN KEY (userID) REFERENCES User(userID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Vendor: subtype of Customer (PK = FK → Customer)
CREATE TABLE Vendor (
  userID     CHAR(36)     NOT NULL,
  bio        TEXT,
  portfolio  VARCHAR(400),
  PRIMARY KEY (userID),
  CONSTRAINT fk_vendor_customer
    FOREIGN KEY (userID) REFERENCES Customer(userID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- ======================
-- DICTIONARY
-- ======================

CREATE TABLE Category (
  categoryID   CHAR(36)     NOT NULL,
  categoryName VARCHAR(50)  NOT NULL UNIQUE,
  description  TEXT,
  PRIMARY KEY (categoryID)
);

-- ======================
-- IMAGE / PURCHASE FLOW
-- ======================

-- Owner is a Vendor (hence FK -> Vendor)
CREATE TABLE Image (
  imageID     CHAR(36)      NOT NULL,
  userID      CHAR(36)      NOT NULL,               -- FK → Vendor
  title       VARCHAR(100)  NOT NULL,
  description TEXT,
  price       DECIMAL(12,2) NOT NULL,
  currency    ENUM('USD','EUR','AUD') NOT NULL DEFAULT 'USD',
  updateDate  DATE,
  imageStatus ENUM('Active','Draft') NOT NULL DEFAULT 'Active',
  quantity    INT            NOT NULL DEFAULT 0,
  extension   VARCHAR(10)    NOT NULL,
  isDeleted   BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (imageID),
  CONSTRAINT fk_img_vendor
    FOREIGN KEY (userID) REFERENCES Vendor(userID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Buyer is any Customer (Vendor qualifies because Vendor ⊂ Customer)
CREATE TABLE Purchase (
  purchaseID   CHAR(36)      NOT NULL,
  userID       CHAR(36)      NOT NULL,               -- FK → Customer
  currency     ENUM('USD','EUR','AUD') NOT NULL DEFAULT 'USD',
  purchaseDate DATE,
  totalAmount  DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (purchaseID),
  CONSTRAINT fk_purchase_customer
    FOREIGN KEY (userID) REFERENCES Customer(userID)
    ON UPDATE CASCADE ON DELETE RESTRICT
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

CREATE TABLE CartImage (
  userID  CHAR(36) NOT NULL,  -- FK → Customer
  imageID CHAR(36) NOT NULL,  -- FK → Image
  PRIMARY KEY (userID, imageID),
  CONSTRAINT fk_cart_customer
    FOREIGN KEY (userID) REFERENCES Customer(userID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_cart_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Rating (
  ratingID   CHAR(36) NOT NULL,
  userID     CHAR(36) NOT NULL,  -- FK → Customer
  imageID    CHAR(36) NOT NULL,  -- FK → Image
  score      INT      NOT NULL,  -- 0..5
  comment    TEXT,
  updateDate DATE,
  PRIMARY KEY (ratingID),
  UNIQUE KEY uq_rating_once (userID, imageID),
  CONSTRAINT chk_score_range CHECK (score >= 0 AND score <= 5),
  CONSTRAINT fk_rating_customer
    FOREIGN KEY (userID) REFERENCES Customer(userID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_rating_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE ImageCategory (
  categoryID CHAR(36) NOT NULL,
  imageID    CHAR(36) NOT NULL,
  PRIMARY KEY (categoryID, imageID),
  KEY idx_ic_image (imageID),
  CONSTRAINT fk_ic_category
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ic_image
    FOREIGN KEY (imageID) REFERENCES Image(imageID)
    ON UPDATE CASCADE ON DELETE CASCADE
);
