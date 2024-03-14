-- UDF
-- Function to calculate the total value of inventory based on price and quantity
CREATE FUNCTION calculate_inventory_value(prod_id INTEGER)
RETURNS DECIMAL
BEGIN
    DECLARE totalInventoryPrice DECIMAL(10,2);

    SELECT SUM(price * inventory) INTO totalInventoryPrice
    FROM product NATURAL JOIN store
    WHERE product_id = prod_id;

    RETURN totalInventoryPrice;
END;


-- PROCEDURE
-- Procedure to update inventory for a specific product in the Store table
CREATE PROCEDURE update_inventory (
    IN product_id CHAR(5),
    IN new_inventory INTEGER
)
BEGIN
    UPDATE store
    SET inventory = new_inventory
    WHERE product_id = product_id;
END;



-- TRIGGER
-- Change delimiter for the trigger creation
DELIMITER !

-- Trigger to update inventory count in the store table after inserting a record into the cart table
CREATE TRIGGER after_insert_cart AFTER INSERT ON cart FOR EACH ROW
BEGIN
    -- Update inventory count in the store table when a product is added to the cart
    UPDATE store
    SET inventory = inventory - NEW.num_items
    WHERE product_id = NEW.product_id;
END;

-- Reset delimiter to semicolon
DELIMITER ;


-- trigger to update inventory on cart checkout
DELIMITER //

CREATE TRIGGER after_insert_cart_checkout AFTER INSERT ON cart FOR EACH ROW
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
END //

DELIMITER ;