# 💅 Cosmetics E-Commerce Project 💅
For Caltech's CS 121 Final Project, we plan to develop an e-commerce application for cosmetics products and brands.

## :memo: Final Project Proposal :memo:
Here's the link to our Final Project Proposal: [Final Project Proposal](https://docs.google.com/document/d/1-SiWRTnO7FuUWw8p5J6z06Gr7R1Q0K7K66yuXgOf-pE/edit?usp=sharing)

## :memo: Final Project Reflection :memo:
[Final Project Reflection](https://docs.google.com/document/d/1Hde-_pKrwx3MjlaA7Wf45lSM-s4AJjjuWSPrywgU4JM/edit?usp=sharing)

## Project Description
For our CS 121 Final Project, we have worked on creating a cosmetics e-commerce application where the users can browse and purchase items from.

### Run our application

1. Running our database

In `mysql`, run the following:
```
CREATE DATABASE cosmeticsdb;
USE cosmeticsdb;
SOURCE setup.sql;
SOURCE load-data.sql;
SOURCE setup-passwords.sql;
SOURCE setup-routines.sql;
SOURCE grant-permissions.sql;
SOURCE queries.sql;
```

2. Running our client-side application

Our client application has been implemented using Python's Flask framework. To run the app, you must install required libraries. Run the following commands (assuming you are at the root directory, CS121FinalProject):
```
cd webClientInterface
```
if you have Python 3:
```
pip3 install requirements.txt
flask --app app ru
```
if you have Python 2:
```
pip install requirements.txt
flask --app app run
```

Flask will take a bit of time to load (up to several minutes) when its loading for the first time. Even if you get a 404 error, wait for a few minutes and retry. We have attached a demo video of our program for those of you who might want to see our project without downloading/running Flask.

[LINK TO DEMO VIDEO](https://drive.google.com/file/d/15M8fY-DxguPLgQVss1tEQXJ-uzZZRzYS/view?usp=sharing)

### Data
We obtained our data for the project from Kaggle's [Cosmetics datasets](https://www.kaggle.com/datasets/kingabzpro/cosmetics-datasets), which contains a singular file, cosmetics.csv, that contains the following 11 columns: Label (Product type, e.g. Moisturizer), Brand, Name (of the product), Price, Rank (Rating), Ingredients, Combination (boolean value), Dry (boolean), Normal (boolean), Oily (boolean), and Sensitive (boolean).

#### Data Cleaning
Part of our project involved designing an efficient DDL and loading our pre-existing data into our database tables. In order to do so, we have cleaned and pre-processed our data rigorously through either utilizing Excel/Google Sheets or writing a Python Pandas/NumPy program.

1. `brands.csv, products.csv, stores.csv`
- Using Excel, we were able to generate our primary datasets, `brands, products`, and `stores`. These contain unique ids for each, and any attribute associated with them.
- These datasets were generated using Excel tools and were relatively simple to generate

2. `ingredients.csv`
- `ingredients.csv` has been mainly generated using a Python script (`Pandas/NumPy`) and manual processing
- it had a lot of anomaly data and hard-to-detect duplicates (e.g. duplicates in different languages or same ingredients written in different string format), which had to be manually removed
- the initial, raw dataset generated by Pandas script contained about 8500 rows, and through manual cleaning, we narrowed it down to 5800 rows.

3. `product_ingredients.csv`
- `product_ingredients.csv` has also been generated using a Python script
- the script goes through each of the original `ingredients` texts one by one, and loops through all the possible ingredients in our ingredients dataset to find all ingredients that are present in the text
- it then writes to `product_ingredients.csv` file line by line all the pairs of `(product_id, ingredient_id)`



