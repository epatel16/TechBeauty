CREATE TABLE sale (
    sale_id         INTEGER AUTO_INCREMENT,
    brand_id        INTEGER,
    product_type    VARCHAR(50),
    -- what % discount we are giving to the users
    discount        DECIMAL(5, 2) CHECK (discount >= 0 AND discount <= 100),
    PRIMARY KEY (sale_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
        ON DELETE CASCADE
);