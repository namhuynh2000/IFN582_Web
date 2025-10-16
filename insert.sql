USE photosite;

-- =========================
-- USERS (2 admins, 2 vendors, 2 customers)
-- =========================
SET
  @admin1  = UUID(),
  @admin2  = UUID(),
  @vendor1 = UUID(),
  @vendor2 = UUID(),
  @cust1   = UUID(),
  @cust2   = UUID();

INSERT INTO `User`
(userID, username, password, email, firstname, surname, phone, role, customerRank, bio, portfolio, totalSales)
VALUES
-- Admins
(@admin1,  'admin_anne', 'hash_admin1', 'anne@site.test',  'Anne',  'Admin',  '111-111', 'Admin', NULL, NULL, NULL, 0),
(@admin2,  'admin_alan', 'hash_admin2', 'alan@site.test',  'Alan',  'Admin',  '111-112', 'Admin', NULL, NULL, NULL, 0),

-- Vendors (role vẫn là Customer, nhưng có bio & portfolioURL)
(@vendor1, 'vendor_viv', 'hash_vend1',  'viv@site.test',   'Viv',   'Vendor', '222-201', 'Customer', NULL, 'Nature photographer', 'https://portfolio.example/viv', 0),
(@vendor2, 'vendor_val', 'hash_vend2',  'val@site.test',   'Val',   'Vendor', '222-202', 'Customer', NULL, 'City & abstract artist', 'https://portfolio.example/val', 0),

-- Customers
(@cust1,   'cust_cara',  'hash_cus1',   'cara@site.test',  'Cara',  'Cust',   '333-301', 'Customer', 'Bronze', NULL, NULL, 0),
(@cust2,   'cust_carl',  'hash_cus2',   'carl@site.test',  'Carl',  'Cust',   '333-302', 'Customer', 'Gold',   NULL, NULL, 0);

-- =========================
-- CATEGORIES
-- =========================
SET
  @cat_nature   = UUID(),
  @cat_city     = UUID(),
  @cat_abstract = UUID();

INSERT INTO Category (categoryID, categoryName, description) VALUES
(@cat_nature,   'Nature',   'Landscapes, animals, outdoors.'),
(@cat_city,     'City',     'Architecture and street scenes.'),
(@cat_abstract, 'Abstract', 'Patterns and abstracts.');

-- =========================
-- IMAGES (15 items)
-- =========================
SET
  @img1  = UUID(), @img2  = UUID(), @img3  = UUID(), @img4  = UUID(), @img5  = UUID(),
  @img6  = UUID(), @img7  = UUID(), @img8  = UUID(), @img9  = UUID(), @img10 = UUID(),
  @img11 = UUID(), @img12 = UUID(), @img13 = UUID(), @img14 = UUID(), @img15 = UUID();

-- Vendor1 (Nature)
INSERT INTO Image (imageID, userID, title, description, price, currency, updateDate, imageStatus, quantity, extension) VALUES
(@img1,  @vendor1, 'Sunrise Ridge', 'Golden sunrise over hills',  19.99, 'USD', '2025-10-01', 'Active', 100, '.png'),
(@img2,  @vendor1, 'Forest Path',   'Misty forest trail',         14.50, 'USD', '2025-09-28', 'Active', 100, '.png'),
(@img3,  @vendor1, 'Ocean Wave',    'Crashing wave close-up',     17.25, 'USD', '2025-09-25', 'Active', 100, '.png'),
(@img4,  @vendor1, 'Autumn Leaves', 'Fallen leaves macro',        12.00, 'USD', '2025-09-20', 'Active', 100, '.png'),
(@img5,  @vendor1, 'Mountain Peak', 'Snowy summit',               21.99, 'USD', '2025-09-18', 'Active', 100, '.png');

-- Vendor2 (City)
INSERT INTO Image (imageID, userID, title, description, price, currency, updateDate, imageStatus, quantity, extension) VALUES
(@img6,  @vendor2, 'Night Avenue', 'City avenue at night',        15.99, 'USD', '2025-09-30', 'Active', 100, '.png'),
(@img7,  @vendor2, 'Old Bridge',   'Historic bridge span',        13.49, 'USD', '2025-09-27', 'Active', 100, '.png'),
(@img8,  @vendor2, 'Metro Lines',  'Subway long exposure',        16.75, 'USD', '2025-09-23', 'Active', 100, '.png'),
(@img9,  @vendor2, 'Neon Alley',   'Neon-lit alley',              11.50, 'USD', '2025-09-19', 'Active', 100, '.png'),
(@img10, @vendor2, 'City Sunset',  'Skyline silhouette',          18.20, 'USD', '2025-09-15', 'Active', 100, '.png');

-- Vendor2 (Abstract)
INSERT INTO Image (imageID, userID, title, description, price, currency, updateDate, imageStatus, quantity, extension) VALUES
(@img11, @vendor2, 'Glass Prism',  'Prismatic colors',             9.99, 'USD', '2025-09-10', 'Active', 100, '.png'),
(@img12, @vendor2, 'Oil Swirl',    'Liquid abstract',              8.50, 'USD', '2025-09-08', 'Active', 100, '.png'),
(@img13, @vendor2, 'Paper Folds',  'Monochrome folds',             7.75, 'USD', '2025-09-05', 'Active', 100, '.png'),
(@img14, @vendor2, 'Light Trails', 'Long-exposure trails',        10.25, 'USD', '2025-09-03', 'Active', 100, '.png'),
(@img15, @vendor2, 'Color Grid',   'Geometric palette',            9.25, 'USD', '2025-09-01', 'Active', 100, '.png');

-- =========================
-- IMAGE CATEGORIES
-- =========================
INSERT INTO ImageCategory (categoryID, imageID) VALUES
-- Nature
(@cat_nature, @img1), (@cat_nature, @img2), (@cat_nature, @img3), (@cat_nature, @img4), (@cat_nature, @img5),
-- City
(@cat_city, @img6), (@cat_city, @img7), (@cat_city, @img8), (@cat_city, @img9), (@cat_city, @img10),
-- Abstract
(@cat_abstract, @img11), (@cat_abstract, @img12), (@cat_abstract, @img13), (@cat_abstract, @img14), (@cat_abstract, @img15);

-- =========================
-- PURCHASES + ITEMS
-- =========================
SET @pur1 = UUID(), @pur2 = UUID(), @pur3 = UUID();

INSERT INTO Purchase (purchaseID, userID, currency, purchaseDate, totalAmount)
VALUES
(@pur1, @cust1, 'USD', '2025-10-05', (19.99 + 15.99)),
(@pur2, @cust2, 'USD', '2025-10-06', (9.99 + 8.50 + 10.25)),
(@pur3, @cust1, 'USD', '2025-10-07', (14.50 + 21.99));

INSERT INTO PurchaseImage (purchaseID, imageID) VALUES
(@pur1, @img1), (@pur1, @img6),
(@pur2, @img11), (@pur2, @img12), (@pur2, @img14),
(@pur3, @img2), (@pur3, @img5);

-- =========================
-- RATINGS
-- =========================
SET @r1 = UUID(), @r2 = UUID(), @r3 = UUID(), @r4 = UUID(), @r5 = UUID(), @r6 = UUID();

INSERT INTO Rating (ratingID, userID, imageID, score, comment, updateDate) VALUES
(@r1, @cust1, @img1, 5, 'Great composition', '2025-10-08'),
(@r2, @cust1, @img6, 4, 'Nice color tones',  '2025-10-08'),
(@r3, @cust1, @img5, 5, 'Stunning peak!',    '2025-10-09'),
(@r4, @cust2, @img11,4, 'Lovely prism',      '2025-10-08'),
(@r5, @cust2, @img12,3, 'Good texture',      '2025-10-08'),
(@r6, @cust2, @img14,5, 'Fantastic trails',  '2025-10-09');

-- =========================
-- CART
-- =========================
INSERT INTO CartImage (userID, imageID) VALUES
(@cust1, @img8), (@cust1, @img12),
(@cust2, @img5), (@cust2, @img9);
