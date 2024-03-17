# 💅 Cosmetics E-Commerce Project 💅
For Caltech's CS 121 Final Project, we plan to develop an e-commerce application for cosmetics products and brands.

## :memo: Final Project Proposal :memo:
Here's the link to our Final Project Proposal: [Final Project Proposal](https://docs.google.com/document/d/1-SiWRTnO7FuUWw8p5J6z06Gr7R1Q0K7K66yuXgOf-pE/edit?usp=sharing)

## :memo: Final Project Reflection :memo:
[Final Project Reflection](https://docs.google.com/document/d/1Hde-_pKrwx3MjlaA7Wf45lSM-s4AJjjuWSPrywgU4JM/edit?usp=sharing)

## Project Description
For our CS 121 Final Project, we have worked on creating a cosmetics e-commerce application where the users can browse and purchase items from.

### Data
We obtained our data for the project from Kaggle's [Cosmetics datasets](https://www.kaggle.com/datasets/kingabzpro/cosmetics-datasets), which contains a singular file, cosmetics.csv, that contains the following 11 columns: Label (Product type, e.g. Moisturizer), Brand, Name (of the product), Price, Rank (Rating), Ingredients, Combination (boolean value), Dry (boolean), Normal (boolean), Oily (boolean), and Sensitive (boolean).

#### Data Cleaning
Part of our project involved designing an efficient DDL and loading our pre-existing data into our database tables. In order to do so, we have cleaned and pre-processed our data rigorously through either utilizing Excel/Google Sheets or writing a Python Pandas/NumPy program.

1. brands.csv, products.csv



## How to run our code

1. Running our database
```
source setup.sql;
source load-data.sql;
source setup-passwords.sql;
source setup-routines.sql;
source grant-permissions.sql;
source queries.sql;
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


## Application Description


## Schema Diagram
<img width="425" alt="Screenshot 2024-02-28 at 9 07 18 PM" src="https://github.com/subinkim/CS121FinalProject/assets/11864278/6dcf3e88-f3fe-4c82-b693-13426b56aba9">

## Example Flowchart
<img width="336" alt="Screenshot 2024-02-28 at 9 07 03 PM" src="https://github.com/subinkim/CS121FinalProject/assets/11864278/f41efc1f-c7ef-4900-8f22-bba2dedec841">
