-- UDF
-- Function to calculate the total value of inventory based on price and quantity
DROP FUNCTION IF EXISTS calculate_inventory_value;
DELIMITER !
CREATE FUNCTION calculate_inventory_value(prod_id INTEGER)
RETURNS DECIMAL DETERMINISTIC
BEGIN
    DECLARE totalInventoryPrice DECIMAL(10,2);

    SELECT SUM(price * inventory) INTO totalInventoryPrice
    FROM product NATURAL JOIN store
    WHERE product_id = prod_id;

    RETURN totalInventoryPrice;
END !
DELIMITER ;

-- Function to calculate the total value of the cart
DROP FUNCTION IF EXISTS calculate_cart_total;
DELIMITER !
CREATE FUNCTION calculate_cart_total(username VARCHAR(20))
RETURNS DECIMAL DETERMINISTIC
BEGIN
    DECLARE totalCartPrice DECIMAL(10,2);

    SELECT SUM(price * num_items) INTO totalCartPrice
    FROM cart NATURAL JOIN product NATURAL JOIN store
    WHERE username=username;

    RETURN totalCartPrice;
END !
DELIMITER ;

-- PROCEDURE
-- Procedure to update inventory for a specific product in the Store table
-- This is an admin privelage
DROP PROCEDURE IF EXISTS update_inventory;
DELIMITER !
CREATE PROCEDURE update_inventory (
    IN product_id CHAR(5),
    IN new_inventory INTEGER
)
BEGIN
    UPDATE store
    SET inventory = new_inventory
    WHERE product_id = product_id;
END !
DELIMITER ;

-- Procedure to remove items from cart for a specific user and add the
-- info to purchase_history table
DROP PROCEDURE IF EXISTS move_cart_to_purchase_history;
DELIMITER !
CREATE PROCEDURE move_cart_to_purchase_history(
    IN p_username VARCHAR(20)
)
BEGIN
    -- Insert items from cart to purchase_history
    INSERT INTO purchase_history (username, purchase_time, product_id, num_items)
    SELECT username, NOW() AS purchase_time, product_id, num_items
    FROM cart WHERE username = p_username;
        
    -- Delete items from cart
    DELETE FROM cart WHERE username = p_username;
END !
DELIMITER ;

-- Procedure to add item to cart and check that there is enough inventory left
DROP PROCEDURE IF EXISTS add_item_cart;
DELIMITER !
CREATE PROCEDURE add_item_cart(
    IN p_username VARCHAR(20),
    IN p_product_id INT
)
BEGIN
    -- Check if the product exists
    DECLARE available_quantity INT;
    
    -- Check if the requested quantity is available in the store
    SELECT inventory INTO available_quantity
    FROM store WHERE product_id = p_product_id;
    
    IF available_quantity = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product is out of stock';
    ELSE
        -- Insert the item into the cart
        INSERT INTO cart (username, product_id, num_items)
        VALUES (p_username, p_product_id, 1)
        ON DUPLICATE KEY UPDATE num_items = num_items + 1;
    END IF;
END !
DELIMITER ;


-- TRIGGER

-- trigger to update inventory on user checks out items in their cart
DROP TRIGGER IF EXISTS after_cart_checkout;
DELIMITER !
CREATE TRIGGER after_cart_checkout AFTER INSERT ON cart FOR EACH ROW
BEGIN
    DECLARE product_id_var INTEGER;
    DECLARE num_items_var SMALLINT;

    -- Fetch cart items for the inserted user
    SELECT product_id, num_items
    INTO product_id_var, num_items_var
    FROM cart NATURAL JOIN user_info
    WHERE username = NEW.username;

    -- Update inventory for the product
    UPDATE store
    SET inventory = inventory - num_items_var
    WHERE product_id = product_id_var;
END !
DELIMITER ;

-- checkout trigger needs to be called before move procedure