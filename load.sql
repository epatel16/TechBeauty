-- brand csv loading
LOAD DATA LOCAL INFILE 'data/brands.csv' INTO TABLE brand
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- product csv loading
LOAD DATA LOCAL INFILE 'data/products.csv' INTO TABLE product
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- skin_preference csv loading
LOAD DATA LOCAL INFILE 'data/stores.csv' INTO TABLE store
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- ingredients csv loading
LOAD DATA LOCAL INFILE 'data/ingredients.csv' INTO TABLE ingredient
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 ROWS;

-- has_ingredient csv loading
LOAD DATA LOCAL INFILE 'data/product_ingredients.csv' INTO TABLE has_ingredient
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;