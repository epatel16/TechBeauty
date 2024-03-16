-- This is a small file to set up MySQL users with different privileges using GRANT statements, 
-- referring to the client and admin user(s) you identified in the Project Proposal.
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'adminpwd';
CREATE USER 'client'@'localhost' IDENTIFIED BY 'clientpwd';

GRANT ALL PRIVILEGES ON cosmeticsdb.* TO 'admin'@'localhost';

GRANT SELECT ON cosmeticsdb.* TO 'client'@'localhost';


GRANT EXECUTE ON cosmeticsdb.* TO 'client'@'localhost';

-- GRANT EXECUTE ON FUNCTION cosmeticsdb.make_salt TO 'client'@'localhost';
-- GRANT EXECUTE ON PROCEDURE cosmeticsdb.sp_add_user TO 'client'@'localhost';
-- GRANT EXECUTE ON FUNCTION cosmeticsdb.authenticate TO 'client'@'localhost';
-- GRANT EXECUTE ON PROCEDURE cosmeticsdb.sp_change_password TO 'client'@'localhost';

-- GRANT EXECUTE ON PROCEDURE cosmeticsdb.move_cart_to_purchase_history TO 'client'@'localhost';
-- GRANT EXECUTE ON PROCEDURE cosmeticsdb.add_item_cart TO 'client'@'localhost';
-- GRANT EXECUTE ON TRIGGER cosmeticsdb.after_cart_checkout TO 'client'@'localhost';

FLUSH PRIVILEGES;
