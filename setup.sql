DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS skin_preference;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS user;

-- Create Brand table, which contains information about
-- information about each brand on the store
CREATE TABLE brand (
    -- brand_id is formatted in the following way: BRx
    -- where x is a number from 1 to 116.
    brand_id    VARCHAR(5),
    brand_name  VARCHAR(100) NOT NULL,
    PRIMARY KEY (brand_id)
);

-- Create Product table, which contains information about
CREATE TABLE product (
    product_id      INTEGER,
    brand_id        VARCHAR(5),
    product_name    VARCHAR(200) NOT NULL,
    product_type    VARCHAR(50),
    ingredients     TEXT,
    price           DECIMAL(10,2) CHECK (price >= 0),
    -- Starting inventory is a randomly generated number
    -- between 10 and 120
    inventory       INTEGER,
    rating          DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    PRIMARY KEY (product_id, brand_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
);

-- Create Skin Preference table, which contains the skin preference
-- type for each product, identified by using either 0 or 1 for each
-- skin preference.
CREATE TABLE skin_preference (
    product_id       INTEGER,
    is_combination   TINYINT DEFAULT 0,
    is_normal        TINYINT DEFAULT 0,
    is_dry           TINYINT DEFAULT 0,
    is_oily          TINYINT DEFAULT 0,
    is_sensit        TINYINT DEFAULT 0,
    PRIMARY KEY (product_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Create User table which stores the username and
-- password for each user, which users will use for authentication.
CREATE TABLE user (
    user_id     INTEGER AUTO_INCREMENT,
    username    VARCHAR(15) NOT NULL,
    password    VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_id)
);

-- Create Cart table which stores users' shopping cart
-- (e.g. products users intend to purchase, and the number
-- of each product that they plan to purchase)
CREATE TABLE cart (
    user_id      INTEGER,
    product_id   INTEGER,
    num_items    SMALLINT,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
