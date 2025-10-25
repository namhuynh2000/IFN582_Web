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
-- ========================= INSERTS
-- =========================
USE photosite;

-- =========================
-- USERS (2 admins, 2 vendors, 2 customers)
-- SHA-256 of:
--   admin_anne: Admin#1!  -> 5bd1e878e66650efa8769016456761f6ff541692929f84f7afb46ba323934a69
--   admin_alan: Admin#2!  -> 97d258f5b838162b96517f5643884916e948a0f0fba95c457a9484fac8f09acd
--   vendor_viv: Vend0r#1  -> 921a447b6ea9b740f4b03b18008a1a3e930e927bf6d24edeca3e964c2d594b9a
--   vendor_val: Vend0r#2  -> 9c3104df92ee9fa72c39070d102ad281d9eb4d99fa83c99cd1a01ebf1ab3399b
--   cust_cara : Cust#1$   -> 1e22b47bbf4f9503ddaaf6a125459782967f0f18b02309190ae723c6fe051dc3
--   cust_carl : Cust#2$   -> 2cdf399bcc538fd0837003cfe6fbe4d5926c99029debf012ddf6dcd08e96fc7c
INSERT INTO `User` (userID, username, password, email, firstname, surname, phone, role, isDeleted) VALUES
('c8dab17c-ee7b-4afa-a147-e996e4bc5d05','admin_anne','5bd1e878e66650efa8769016456761f6ff541692929f84f7afb46ba323934a69','anne@site.test','Anne','Admin','111-111','Admin',FALSE),
('66fa9c21-d5dc-4bc4-ba23-7f6832562c3c','admin_alan','97d258f5b838162b96517f5643884916e948a0f0fba95c457a9484fac8f09acd','alan@site.test','Alan','Admin','111-112','Admin',FALSE),
('d2c29738-9369-49e9-a139-83e9ce2837ac','vendor_viv','921a447b6ea9b740f4b03b18008a1a3e930e927bf6d24edeca3e964c2d594b9a','viv@site.test','Viv','Vendor','222-201','Vendor',FALSE),
('410076b5-6eef-4439-ba38-c4bb3683e228','vendor_val','9c3104df92ee9fa72c39070d102ad281d9eb4d99fa83c99cd1a01ebf1ab3399b','val@site.test','Val','Vendor','222-202','Vendor',FALSE),
('12bacf34-5848-46b8-826b-c5b7084fc72a','cust_cara','1e22b47bbf4f9503ddaaf6a125459782967f0f18b02309190ae723c6fe051dc3','cara@site.test','Cara','Cust','333-301','Customer',FALSE),
('e4face8e-0a91-40c8-9090-34433e0222c1','cust_carl','2cdf399bcc538fd0837003cfe6fbe4d5926c99029debf012ddf6dcd08e96fc7c','carl@site.test','Carl','Cust','333-302','Customer',TRUE);

-- Admin profiles
INSERT INTO Admin (userID) VALUES
('c8dab17c-ee7b-4afa-a147-e996e4bc5d05'),
('66fa9c21-d5dc-4bc4-ba23-7f6832562c3c');

-- Customers (vendors are also customers)
INSERT INTO Customer (userID, customerRank) VALUES
('d2c29738-9369-49e9-a139-83e9ce2837ac','Silver'),
('410076b5-6eef-4439-ba38-c4bb3683e228','Gold'),
('12bacf34-5848-46b8-826b-c5b7084fc72a','Bronze'),
('e4face8e-0a91-40c8-9090-34433e0222c1','Gold');

-- Vendor profiles
INSERT INTO Vendor (userID, bio, portfolio) VALUES
('d2c29738-9369-49e9-a139-83e9ce2837ac','Nature photographer','https://portfolio.example/viv'),
('410076b5-6eef-4439-ba38-c4bb3683e228','City & abstract visual artist','https://portfolio.example/val');

-- =========================
-- CATEGORIES
INSERT INTO Category (categoryID, categoryName, description) VALUES
('2953514c-5d5b-487f-8980-45b0c484fd20','Nature','Landscapes, animals, outdoors.'),
('57ec2632-fe22-4277-9c71-b83455d5aef6','City','Architecture and street scenes.'),
('45836d76-fcb9-481c-b585-d0d656d8bc04','Abstract','Patterns and abstracts.');

-- =========================
-- IMAGES (15 items) owned by Vendors, with isDeleted
INSERT INTO Image (imageID, userID, title, description, price, currency, updateDate, imageStatus, quantity, extension, isDeleted) VALUES
('59fa8933-4171-4c4e-a548-6b2320703c15','d2c29738-9369-49e9-a139-83e9ce2837ac','Sunrise Ridge','Golden sunrise over hills',19.99,'USD','2025-10-01','Active',12,'.png',FALSE),
('8d869d66-74ad-4276-95a0-80bf42ee037e','d2c29738-9369-49e9-a139-83e9ce2837ac','Forest Path','Misty forest trail',14.50,'USD','2025-09-28','Active',32,'.png',FALSE),
('7b636900-faff-400f-b3ea-7cb7ce386c60','d2c29738-9369-49e9-a139-83e9ce2837ac','Ocean Wave','Crashing wave close-up',17.25,'USD','2025-09-25','Active',2,'.png',FALSE),
('1282041d-ef1c-429b-bbfd-bf7b69710012','d2c29738-9369-49e9-a139-83e9ce2837ac','Autumn Leaves','Fallen leaves macro',12.00,'USD','2025-09-20','Active',43,'.png',FALSE),
('4744f11c-d328-49c9-a86b-65e6f949f795','d2c29738-9369-49e9-a139-83e9ce2837ac','Mountain Peak','Snowy summit',21.99,'USD','2025-09-18','Active',55,'.png',FALSE),

('ddf28e71-787b-4877-ac46-eff72c44bd46','410076b5-6eef-4439-ba38-c4bb3683e228','Night Avenue','City avenue at night',15.99,'USD','2025-09-30','Active',12,'.png',FALSE),
('3ab6a7a2-27fd-407e-a7e6-a2d42340071d','410076b5-6eef-4439-ba38-c4bb3683e228','Old Bridge','Historic bridge span',13.49,'USD','2025-09-27','Active',43,'.png',FALSE),
('e8b0d24b-e820-434d-a249-13365c8d8889','410076b5-6eef-4439-ba38-c4bb3683e228','Metro Lines','Subway long exposure',16.75,'USD','2025-09-23','Active',2,'.png',FALSE),
('13395274-3e56-4df3-b5d6-b19198ab3862','410076b5-6eef-4439-ba38-c4bb3683e228','Neon Alley','Neon-lit alley',11.50,'USD','2025-09-19','Active',66,'.png',FALSE),
('a058a058-ca2c-4564-8b26-cbb3dd5ddace','410076b5-6eef-4439-ba38-c4bb3683e228','City Sunset','Skyline silhouette',18.20,'USD','2025-09-15','Active',122,'.png',FALSE),

('576f7c91-5438-4a94-9ac2-57a556287de1','410076b5-6eef-4439-ba38-c4bb3683e228','Glass Prism','Prismatic colors',9.99,'USD','2025-09-10','Active',4,'.png',FALSE),
('7614f542-34db-4646-a4e8-4d4ea51bb57e','410076b5-6eef-4439-ba38-c4bb3683e228','Oil Swirl','Liquid abstract',8.50,'USD','2025-09-08','Active',5,'.png',FALSE),
('a739489b-dcef-42bd-aa65-2e12e19fb6e8','410076b5-6eef-4439-ba38-c4bb3683e228','Paper Folds','Monochrome folds',7.75,'USD','2025-09-05','Active',86,'.png',FALSE),
('5d4c555e-5c00-4292-9fc7-8e5ce8f27453','410076b5-6eef-4439-ba38-c4bb3683e228','Light Trails','Long-exposure trails',10.25,'USD','2025-09-03','Active',2,'.png',FALSE),
('1acc0192-cb36-49c5-ad30-565102b885ce','410076b5-6eef-4439-ba38-c4bb3683e228','Color Grid','Geometric palette',9.25,'USD','2025-09-01','Active',1,'.png',FALSE);

-- =========================
-- IMAGE ↔ CATEGORY
INSERT INTO ImageCategory (categoryID, imageID) VALUES
('2953514c-5d5b-487f-8980-45b0c484fd20','59fa8933-4171-4c4e-a548-6b2320703c15'),
('2953514c-5d5b-487f-8980-45b0c484fd20','8d869d66-74ad-4276-95a0-80bf42ee037e'),
('2953514c-5d5b-487f-8980-45b0c484fd20','7b636900-faff-400f-b3ea-7cb7ce386c60'),
('2953514c-5d5b-487f-8980-45b0c484fd20','1282041d-ef1c-429b-bbfd-bf7b69710012'),
('2953514c-5d5b-487f-8980-45b0c484fd20','4744f11c-d328-49c9-a86b-65e6f949f795'),

('57ec2632-fe22-4277-9c71-b83455d5aef6','ddf28e71-787b-4877-ac46-eff72c44bd46'),
('57ec2632-fe22-4277-9c71-b83455d5aef6','3ab6a7a2-27fd-407e-a7e6-a2d42340071d'),
('57ec2632-fe22-4277-9c71-b83455d5aef6','e8b0d24b-e820-434d-a249-13365c8d8889'),
('57ec2632-fe22-4277-9c71-b83455d5aef6','13395274-3e56-4df3-b5d6-b19198ab3862'),
('57ec2632-fe22-4277-9c71-b83455d5aef6','a058a058-ca2c-4564-8b26-cbb3dd5ddace'),

('45836d76-fcb9-481c-b585-d0d656d8bc04','576f7c91-5438-4a94-9ac2-57a556287de1'),
('45836d76-fcb9-481c-b585-d0d656d8bc04','7614f542-34db-4646-a4e8-4d4ea51bb57e'),
('45836d76-fcb9-481c-b585-d0d656d8bc04','a739489b-dcef-42bd-aa65-2e12e19fb6e8'),
('45836d76-fcb9-481c-b585-d0d656d8bc04','5d4c555e-5c00-4292-9fc7-8e5ce8f27453'),
('45836d76-fcb9-481c-b585-d0d656d8bc04','1acc0192-cb36-49c5-ad30-565102b885ce');

-- =========================
-- PURCHASES (+ items)
INSERT INTO Purchase (purchaseID, userID, purchaseDate, totalAmount) VALUES
('13b922e2-7f7d-4ece-8782-3747d4bf2b25','12bacf34-5848-46b8-826b-c5b7084fc72a','2025-10-05',(19.99 + 15.99)),
('a497b77e-821a-48d6-ab5c-935c43ac9663','e4face8e-0a91-40c8-9090-34433e0222c1','2025-10-06',(9.99 + 8.50 + 10.25)),
('3edae5e8-f652-4edb-8f08-e4a7d2fb6c99','d2c29738-9369-49e9-a139-83e9ce2837ac','2025-10-07',(14.50 + 21.99));

INSERT INTO PurchaseImage (purchaseID, imageID) VALUES
('13b922e2-7f7d-4ece-8782-3747d4bf2b25','59fa8933-4171-4c4e-a548-6b2320703c15'),
('13b922e2-7f7d-4ece-8782-3747d4bf2b25','ddf28e71-787b-4877-ac46-eff72c44bd46'),
('a497b77e-821a-48d6-ab5c-935c43ac9663','576f7c91-5438-4a94-9ac2-57a556287de1'),
('a497b77e-821a-48d6-ab5c-935c43ac9663','7614f542-34db-4646-a4e8-4d4ea51bb57e'),
('a497b77e-821a-48d6-ab5c-935c43ac9663','5d4c555e-5c00-4292-9fc7-8e5ce8f27453'),
('3edae5e8-f652-4edb-8f08-e4a7d2fb6c99','8d869d66-74ad-4276-95a0-80bf42ee037e'),
('3edae5e8-f652-4edb-8f08-e4a7d2fb6c99','4744f11c-d328-49c9-a86b-65e6f949f795');

-- =========================
-- RATINGS
INSERT INTO Rating (ratingID, userID, imageID, score, comment, updateDate) VALUES
('6165c148-06da-4d36-a6b7-65d6571cb810','12bacf34-5848-46b8-826b-c5b7084fc72a','59fa8933-4171-4c4e-a548-6b2320703c15',5,'Great composition','2025-10-08'),
('b431d7a7-392d-4ead-8ef0-c3493ad001a9','12bacf34-5848-46b8-826b-c5b7084fc72a','ddf28e71-787b-4877-ac46-eff72c44bd46',4,'Nice color tones','2025-10-08'),
('11c1d0ab-5dd3-4e9f-abd5-88c4bd91c8cf','d2c29738-9369-49e9-a139-83e9ce2837ac','4744f11c-d328-49c9-a86b-65e6f949f795',5,'Stunning peak!','2025-10-09'),
('255813bd-3e0b-42e0-a841-b28cdef72e68','e4face8e-0a91-40c8-9090-34433e0222c1','576f7c91-5438-4a94-9ac2-57a556287de1',4,'Lovely prism','2025-10-08'),
('b18a073b-79fd-425c-81bc-f24dc5756870','e4face8e-0a91-40c8-9090-34433e0222c1','7614f542-34db-4646-a4e8-4d4ea51bb57e',3,'Good texture','2025-10-08'),
('63bd2fdb-a495-471c-b3e1-ca932000217a','d2c29738-9369-49e9-a139-83e9ce2837ac','5d4c555e-5c00-4292-9fc7-8e5ce8f27453',5,'Fantastic trails','2025-10-09');

-- =========================
-- CART
INSERT INTO CartImage (userID, imageID) VALUES
('12bacf34-5848-46b8-826b-c5b7084fc72a','e8b0d24b-e820-434d-a249-13365c8d8889'),
('12bacf34-5848-46b8-826b-c5b7084fc72a','7614f542-34db-4646-a4e8-4d4ea51bb57e'),
('e4face8e-0a91-40c8-9090-34433e0222c1','4744f11c-d328-49c9-a86b-65e6f949f795'),
('e4face8e-0a91-40c8-9090-34433e0222c1','13395274-3e56-4df3-b5d6-b19198ab3862'),
('410076b5-6eef-4439-ba38-c4bb3683e228','7b636900-faff-400f-b3ea-7cb7ce386c60'),
('410076b5-6eef-4439-ba38-c4bb3683e228','a058a058-ca2c-4564-8b26-cbb3dd5ddace');
