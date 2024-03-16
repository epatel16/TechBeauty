-- Retrieve all products with their brand names
SELECT product_name, brand_name
FROM product NATURAL JOIN store NATURAL JOIN brand;

-- Find products with a specific type 
-- change product_type with input to query for desired type
SELECT product_name, product_type, price FROM product WHERE product_type = 'Moisturizer';

-- Get the total inventory count for each product in the store
SELECT product_name, SUM(inventory) AS total_inventory
FROM product NATURAL JOIN store
GROUP BY product_id, product_name;

-- Retrieve products with a certain rating range
SELECT product_name, price, rating FROM product WHERE rating BETWEEN 3.0 AND 4.5;

-- Find products suitable for oily skin
SELECT product_name, product_type, price FROM product WHERE is_oily = 1;

-- Get the top-rated products
SELECT product_name, price, rating FROM product ORDER BY rating DESC LIMIT 20;

-- Get the all products prices low to high
SELECT product_name, product_type, price, rating FROM product 
WHERE price < 25 ORDER BY price ASC;

-- Retrieve users and their respective shopping carts
SELECT username, product_id, product_name, num_items
FROM user_info NATURAL JOIN cart NATURAL JOIN product;

-- Find users with a specific product in their cart
SELECT username, product_id, product_name, num_items
FROM user_info NATURAL JOIN cart NATURAL JOIN product
WHERE product_name = 'Water Sleeping Mask';

-- Get the number of products in each product type
SELECT product_type, COUNT(*) AS num_products
FROM product GROUP BY product_type;

-- INSERT QUERIES FOR ADMIN
-- Insert data into the brand table for a new brand
INSERT INTO brand (brand_id, brand_name)
VALUES (1, 'NewBrand'); -- Replace with the actual brand name

-- Insert data into the product table for a new product
INSERT INTO product (product_id, product_name, product_type, price,
 rating, is_combination, is_dry, is_normal, is_oily, is_sensitive)
VALUES (
    1,                
    'NewProduct',    
    'Type',           
    19.99,            
    4.5,              
    1,                
    0,               
    1,                
    0,                
    0              
-- Replace the above values with actual values you want to insert
-- Also add to ingredients table accordingly
);

-- Insert data into the store table for the new product and brand
INSERT INTO store (brand_id, product_id, inventory)
VALUES (1, 1, 50); -- Replace with the actual brand_id, product_id, and inventory quantity

-- Insert item into cart when user adds 1
INSERT INTO cart (username, product_id, num_items)
VALUES ('ejpatel', 100, 1);

-- Gets the ingredients of a given product
SELECT ingredient_id, ingredient_name
FROM product NATURAL JOIN has_ingredient
NATURAL JOIN ingredient WHERE product_id = '100';
-- change product id to specify which product you want to see ingredients for