DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS skin_preference;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS user;

-- Create Brand table
CREATE TABLE brand (
    brand_id    CHAR(3) PRIMARY KEY,
    brand_name  VARCHAR(100) NOT NULL
);

-- Create Product table
CREATE TABLE product (
    product_id      CHAR(5) PRIMARY KEY,
    brand_id        CHAR(3),
    inventory       INTEGER,
    product_name    VARCHAR(100) NOT NULL,
    ingredients     TEXT,
    rating          DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    price           DECIMAL(10,2) CHECK (price >= 0),
    product_type    VARCHAR(50),
    PRIMARY KEY (product_id, brand_id)
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
);

-- Create Skin Preference table
CREATE TABLE skin_preference (
    product_id    CHAR(5) PRIMARY KEY,
    combination   TINYINT(1) DEFAULT 0,
    normal        TINYINT(1) DEFAULT 0,
    dry           TINYINT(1) DEFAULT 0,
    oily          TINYINT(1) DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- Create User table
CREATE TABLE user (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(15) NOT NULL,
    password    VARCHAR(15) NOT NULL
);

-- Create Cart table
CREATE TABLE cart (
    user_id      INT,
    product_id   CHAR(5),
    num_items    SMALLINT,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);
