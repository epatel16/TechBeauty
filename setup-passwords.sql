-- CS 121 24wi: Password Management (A6 and Final Project)

-- (Provided) This function generates a specified number of characters for using as a
-- salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt!  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;

-- Provided (you may modify in your FP if you choose)
-- This table holds information for authenticating users based on
-- a password.  Passwords are not stored plaintext so that they
-- cannot be used by people that shouldn't have them.
-- You may extend that table to include an is_admin or role attribute if you
-- have admin or other roles for users in your application
-- (e.g. store managers, data managers, etc.)
-- CREATE TABLE user_info (
--     -- Usernames are up to 20 characters.
--     username VARCHAR(20) PRIMARY KEY,

--     -- Salt will be 8 characters all the time, so we can make this 8.
--     salt CHAR(8) NOT NULL,

--     -- We use SHA-2 with 256-bit hashes.  MySQL returns the hash
--     -- value as a hexadecimal string, which means that each byte is
--     -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
--     -- We can use BINARY or CHAR here; BINARY simply has a different
--     -- definition for comparison/sorting than CHAR.
--     password_hash BINARY(64) NOT NULL
-- );

-- Adds a new user to the user_info table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(new_username VARCHAR(20), password VARCHAR(20))
BEGIN
  DECLARE new_salt VARCHAR(8);
  DECLARE salted_holder VARCHAR(28);
  DECLARE salted_password BINARY(64);

  -- Generate a new salt
  SET new_salt = make_salt(8);

  -- Concatenate salt and password, then hash the string
  SET salted_holder = CONCAT(new_salt, password);
  SET salted_password = SHA2(salted_holder, 256);

  -- Insert the new user into the user_info table
  INSERT INTO user_info 
  VALUES(new_username, new_salt, salted_password);
END !
DELIMITER ;

-- Authenticates the specified username and password against the data
-- in the user_info table.  Returns 1 if the user appears in the table, and the
-- specified password hashes to the value for the user. Otherwise returns 0.
DELIMITER !
CREATE FUNCTION authenticate(username VARCHAR(20), password VARCHAR(20))
RETURNS TINYINT DETERMINISTIC
BEGIN

  -- Declare variables to store salt and hashed password from the database
  DECLARE stored_salt VARCHAR(8);
  DECLARE salted_holder VARCHAR(28);
  DECLARE stored_phash BINARY(64);
  DECLARE salted_password VARCHAR(28);

  -- Check if the username exists in the user_info table
  IF NOT EXISTS(SELECT * FROM user_info WHERE username = username) THEN
        RETURN 0;
  END IF;

  -- Retrieve salt and password hash for the given username
  SELECT salt, password_hash INTO stored_salt, stored_phash
  FROM user_info WHERE user_info.username = username LIMIT 1;

  -- Concatenate stored salt with the provided password and hash the string
  SET salted_holder = CONCAT(stored_salt, password);

  -- Check if the hashed password matches the stored password hash
  IF SHA2(salted_holder, 256) = stored_phash THEN
    RETURN 1; -- Authentication successful
  ELSE
    RETURN 0; -- Incorrect password
  END IF;

END !
DELIMITER ;

-- Create a procedure sp_change_password to generate a new salt and change the given
-- user's password to the given password (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_password(username VARCHAR(20), new_password VARCHAR(20))
BEGIN
  DECLARE new_salt VARCHAR(8);
  DECLARE salted_holder VARCHAR(28);
  DECLARE salted_password BINARY(64);

  -- Generate a new salt 
  SET new_salt = make_salt(8);

  -- Concatenate new salt with the new password, then hash the string
  SET salted_holder = CONCAT(new_salt, new_password);
  SET salted_password = SHA2(salted_holder, 256);

  -- Update the user's password in the user_info table
  UPDATE user_info SET salt = new_salt,
    password_hash = salted_password
  WHERE user_info.username = username;
END !
DELIMITER ;
