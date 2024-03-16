# 💅 Cosmetics E-Commerce Project 💅
For Caltech's CS 121 Final Project, we plan to develop an e-commerce application for cosmetics products and brands.

## :memo: Final Project Proposal :memo:
Here's the link to our Final Project Proposal: [Final Project Proposal](https://docs.google.com/document/d/1-SiWRTnO7FuUWw8p5J6z06Gr7R1Q0K7K66yuXgOf-pE/edit?usp=sharing)

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
