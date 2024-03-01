-- brand csv loading
LOAD DATA LOCAL INFILE 'data/brands.csv' INTO TABLE brand
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- product csv loading
LOAD DATA LOCAL INFILE 'data/products.csv' INTO TABLE product
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- skin_preference csv loading
LOAD DATA LOCAL INFILE 'data/skin_preferences.csv' INTO TABLE skin_preference
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
