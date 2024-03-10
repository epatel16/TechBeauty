DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS user;

-- Create Brand table, which contains information about
-- information about each brand on the store
CREATE TABLE brand (
    brand_id    INTEGER,
    brand_name  VARCHAR(100) NOT NULL,
    PRIMARY KEY (brand_id)
);

-- Create Product table, which contains information about
CREATE TABLE product (
    product_id      INTEGER,
    product_name    VARCHAR(200) NOT NULL,
    product_type    VARCHAR(50),
    ingredients     TEXT,
    price           DECIMAL(10,2) CHECK (price >= 0),
    rating          DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    is_combination  TINYINT DEFAULT 0 
                    CHECK (is_combination = 0 OR is_combination = 1),
    is_dry          TINYINT DEFAULT 0
                    CHECK (is_dry = 0 OR is_dry = 1),
    is_normal       TINYINT DEFAULT 0
                    CHECK (is_normal = 0 OR is_normal = 1),
    is_oily         TINYINT DEFAULT 0
                    CHECK (is_oily = 0 OR is_oily = 1),
    is_sensitive    TINYINT DEFAULT 0
                    CHECK (is_sensitive = 0 OR is_sensitive = 1),
    PRIMARY KEY (product_id)
);

-- Create store table that keeps an inventory of each product 
-- from each brand
CREATE TABLE store (
    brand_id INTEGER,
    product_id INTEGER,
    -- Inventory is randomly generated as an integer between 10 and 120
    inventory INTEGER,
    PRIMARY KEY (brand_id, product_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Create User table which stores the username and
-- password for each user, which users will use for authentication.
CREATE TABLE user (
    user_id     INTEGER AUTO_INCREMENT,
    username    VARCHAR(15) NOT NULL,
    pwd    VARCHAR(20) NOT NULL,
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
