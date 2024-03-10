-- Retrieve all products with their brand names
SELECT product_id, product_name, brand_name
FROM product NATURAL JOIN brand_name;

-- Find products with a specific type
SELECT * FROM product WHERE product_type = 'Lipstick';

-- Get the total inventory count for each product in the store
SELECT product_id, product_name, SUM(inventory) AS total_inventory
FROM product NATURAL JOIN store
GROUP BY product_id, product_name;

-- Retrieve products with a certain rating range
SELECT * FROM product WHERE rating BETWEEN 3.0 AND 4.5;

-- Find products suitable for oily skin
SELECT * FROM product WHERE is_oily = 1;

-- Get the top-rated products
SELECT * FROM product ORDER BY rating DESC LIMIT 20;

-- Retrieve users and their respective shopping carts
SELECT username, product_id, product_name, num_items
FROM user NATURAL JOIN cart NATURAL JOIN product;

-- Find users with a specific product in their cart
SELECT username, product_id, product_name, num_items
FROM user NATURAL JOIN cart NATURAL JOIN product
WHERE product_name = 'Water Sleeping Mask';

-- Get the number of products in each product type
SELECT product_type, COUNT(*) AS num_products
FROM product GROUP BY product_type;