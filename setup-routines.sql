-- UDF
-- Function to calculate the total value of inventory based on price and quantity
CREATE FUNCTION calculate_inventory_value(
    p_price DECIMAL,
    p_quantity DECIMAL)
RETURNS DECIMAL
BEGIN
    DECLARE total_value DECIMAL;
    
    SET total_value = p_price * p_quantity;
    
    RETURN total_value;
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