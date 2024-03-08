-- Retrieve all products with their brand names
SELECT p.product_id, p.product_name, b.brand_name
FROM product p JOIN brand b ON p.brand_id = b.brand_id;

-- Find products with a specific type
SELECT * FROM product WHERE product_type = 'Lipstick';

-- Get the total inventory count for each product in the store
SELECT p.product_id, p.product_name, SUM(s.inventory) AS total_inventory
FROM product p JOIN store s ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name;

-- Retrieve products with a certain rating range
SELECT * FROM product WHERE rating BETWEEN 3.0 AND 4.5;

-- Find products suitable for oily skin
SELECT * FROM product WHERE is_oily = 1;

-- Get the top-rated products
SELECT * FROM product ORDER BY rating DESC LIMIT 20;

-- Retrieve users and their respective shopping carts
SELECT u.username, c.product_id, p.product_name, c.num_items
FROM user u JOIN cart c ON u.user_id = c.user_id
JOIN product p ON c.product_id = p.product_id;

-- Find users with a specific product in their cart
SELECT u.username, c.product_id, p.product_name, c.num_items
FROM user u JOIN cart c ON u.user_id = c.user_id
JOIN product p ON c.product_id = p.product_id
WHERE p.product_name = 'Water Sleeping Mask';

-- Get the number of products in each product type
SELECT product_type, COUNT(*) AS num_products
FROM product GROUP BY product_type;