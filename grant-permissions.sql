-- This is a small file to set up MySQL users with different privileges using GRANT statements, 
-- referring to the client and admin user(s) you identified in the Project Proposal.
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'adminpwd';
CREATE USER 'client'@'localhost' IDENTIFIED BY 'clientpwd';

GRANT ALL PRIVILEGES ON cosmeticsdb.* TO 'admin'@'localhost';

GRANT SELECT ON cosmeticsdb.* TO 'client'@'localhost';

GRANT EXECUTE ON cosmeticsdb.* TO 'client'@'localhost';

FLUSH PRIVILEGES;
