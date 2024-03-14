DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_info;

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
    brand_id    INTEGER,
    product_id  INTEGER,
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
-- CREATE TABLE user (
--     user_id     INTEGER AUTO_INCREMENT,
--     username    VARCHAR(15) NOT NULL,
--     pwd    VARCHAR(20) NOT NULL,
--     PRIMARY KEY (user_id)
-- );

CREATE TABLE user_info (
    -- Usernames are up to 20 characters.
    username VARCHAR(20) PRIMARY KEY,

    -- Salt will be 8 characters all the time, so we can make this 8.
    salt CHAR(8) NOT NULL,

    -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
    -- value as a hexadecimal string, which means that each byte is
    -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
    -- We can use BINARY or CHAR here; BINARY simply has a different
    -- definition for comparison/sorting than CHAR.
    password_hash BINARY(64) NOT NULL
);


-- Create Cart table which stores users' shopping cart
-- (e.g. products users intend to purchase, and the number
-- of each product that they plan to purchase)
CREATE TABLE cart (
    username     VARCHAR(20),
    product_id   INTEGER,
    num_items    SMALLINT,
    PRIMARY KEY (username, product_id),
    FOREIGN KEY (username) REFERENCES user_info(username)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Create purchase history table which stores users' previous purchase
-- (e.g. products users purchased, the id of the purchase
-- and the number of each product they purchased)
CREATE TABLE purchase_history (
    username        VARCHAR(20),
    purchase_time   TIMESTAMP,
    product_id      INTEGER,
    num_items       SMALLINT,
    PRIMARY KEY (username, product_id),
    FOREIGN KEY (username) REFERENCES user_info(username)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Create Sale table tha
CREATE TABLE sale (
    sale_id         INTEGER PRIMARY KEY AUTO_INCREMENT,
    brand_id        INTEGER,
    product_type    VARCHAR(50),
    discount        DECIMAL(5, 2) CHECK (discount >= 0 AND discount <= 100),
    PRIMARY KEY (sale_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);


