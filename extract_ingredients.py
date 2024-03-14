# Python code to generate ingredients data

import pandas as pd
import numpy as np

# unpack cosmetics.csv
# df = pd.read_csv('data/cosmetics.csv')

# df = df[['Product ID', 'Ingredients']]
# print(df)

# # split ingredients texts to create a dataframe
# df_ing = df["Ingredients"].str.split(',', expand=True)
# print(df_ing)

# # extract unique ingredient values
# ingredients = set()

# for col in df_ing:
#     ingredients.update(set(df_ing[col].unique()))

# ingredients.remove("")

# # write ingredient.csv
# indices = [i for i in range(1, len(ingredients) + 1)]
# df_indices = pd.DataFrame(indices, columns=['Ingredient ID'])
# df_final = pd.DataFrame(list(ingredients), columns=['Ingredient'])
# df = pd.concat([df_indices, df_final], axis=1)
# print(df)
# df.to_csv("data/ingredients.csv", index=False)

# Once you get here, you must go through ingredients.csv
# and manually clean the data to remove any foreign langauge
# duplicates, regular duplicates, regular texts that are not
# ingredients, etc.

cos_df = pd.read_csv('data/cosmetics.csv')
cos_df = cos_df[['Product ID', 'Ingredients']]
ing_df = pd.read_csv('data/ingredients.csv')
res = {}

import csv
with open('data/product_ingredients.csv', 'w', newline='') as csvfile:
    fieldnames = ['Product ID', 'Ingredient ID']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for index, row in cos_df.iterrows():
        for idx, r in ing_df.iterrows():
            if r['Ingredient'].lower() in row['Ingredients'].lower():
                writer.writerow({'Product ID': row['Product ID'], 'Ingredient ID': r['Ingredient ID']})