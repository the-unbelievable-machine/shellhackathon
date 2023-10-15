#!/usr/bin/env python
# coding: utf-8

# ## Examples: Stigler diet 
# 
# Which quantities a 70kg male would have to consume from 77 different foods to 
# - fulfill the recommended intake of 9 different nutrients in 1943 
# - keeping expense at a minimum (prices from 1939)
# 
# LP solved by trial and error (before Simplex) by Stigler in 1945.
# 
# See
# - https://en.wikipedia.org/wiki/Stigler_diet
# - https://www.kaggle.com/code/nicapotato/optimisation-101-with-or-tools/notebook

# ## Examples: Stigler diet 2
# 
# Later Dantzig 
# - improved Stiglers solution with Simplex algorithm
# - tried to find the optimal diet to loose weight with Simplex on a computer. 
# 
# He failed (because he didn't include upper limit constraints)
# - Computer recommended ridiculous amounts of apple cider, bran, boullion cubes
# - His wifes diet for him was superior and he lost 11 kg
# 
# See
# - Dantzig (1990): The Diet Problem

# In[ ]:


from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit

# Create the linear solver with the GLOP (the Google Linear Optimization Package) backend (advanced simplex)
# see https://en.wikipedia.org/wiki/GLOP
solver = pywraplp.Solver.CreateSolver('GLOP')


# # Stiglers diet with OR-Tools
# 
# 
# Minimize the sum of money in dollar spent on food $f_i$ for $i=1..77$
# $$
# min \sum_i f_i 
# $$
# The contraints are that the sum of all nutrients in the purchased food $i$ must be bigger than the minimum for each nutrient $n_j$ for $j=1..9$.
# $$
# \sum_i f_i * \text{nutrient_per_dollar}_{ij} \geq n_j
# $$
# So we have a LP problem with 77 variables and 9 constraints.
# 

# In[ ]:


import pandas as pd

print("Define Table..")
# Nutrient minimums.
nutrients = [['Calories (kcal)', 3], ['Protein (g)', 70], [
    'Calcium (g)', 0.8
], ['Iron (mg)', 12], ['Vitamin A (KIU)', 5], ['Vitamin B1 (mg)', 1.8],
             ['Vitamin B2 (mg)', 2.7], ['Niacin (mg)',
                                        18], ['Vitamin C (mg)', 75]]

# Commodity, Unit, 1939 price (cents), Calories (kcal), Protein (g), Calcium (g), Iron (mg),
# Vitamin A (KIU), Vitamin B1 (mg), Vitamin B2 (mg), Niacin (mg), Vitamin C (mg)
data = [[
    'Wheat Flour (Enriched)', '10 lb.', 36, 44.7, 1411, 2, 365, 0, 55.4,
    33.3, 441, 0
], ['Macaroni', '1 lb.', 14.1, 11.6, 418, 0.7, 54, 0, 3.2, 1.9, 68, 0], [
    'Wheat Cereal (Enriched)', '28 oz.', 24.2, 11.8, 377, 14.4, 175, 0,
    14.4, 8.8, 114, 0
], ['Corn Flakes', '8 oz.', 7.1, 11.4, 252, 0.1, 56, 0, 13.5, 2.3, 68, 0], [
    'Corn Meal', '1 lb.', 4.6, 36.0, 897, 1.7, 99, 30.9, 17.4, 7.9, 106, 0
], [
    'Hominy Grits', '24 oz.', 8.5, 28.6, 680, 0.8, 80, 0, 10.6, 1.6, 110, 0
], ['Rice', '1 lb.', 7.5, 21.2, 460, 0.6, 41, 0, 2, 4.8, 60, 0], [
    'Rolled Oats', '1 lb.', 7.1, 25.3, 907, 5.1, 341, 0, 37.1, 8.9, 64, 0
], [
    'White Bread (Enriched)', '1 lb.', 7.9, 15.0, 488, 2.5, 115, 0, 13.8,
    8.5, 126, 0
], [
    'Whole Wheat Bread', '1 lb.', 9.1, 12.2, 484, 2.7, 125, 0, 13.9, 6.4,
    160, 0
], ['Rye Bread', '1 lb.', 9.1, 12.4, 439, 1.1, 82, 0, 9.9, 3, 66, 0], [
    'Pound Cake', '1 lb.', 24.8, 8.0, 130, 0.4, 31, 18.9, 2.8, 3, 17, 0
], ['Soda Crackers', '1 lb.', 15.1, 12.5, 288, 0.5, 50, 0, 0, 0, 0, 0], [
    'Milk', '1 qt.', 11, 6.1, 310, 10.5, 18, 16.8, 4, 16, 7, 177
], [
    'Evaporated Milk (can)', '14.5 oz.', 6.7, 8.4, 422, 15.1, 9, 26, 3,
    23.5, 11, 60
], ['Butter', '1 lb.', 30.8, 10.8, 9, 0.2, 3, 44.2, 0, 0.2, 2, 0], [
    'Oleomargarine', '1 lb.', 16.1, 20.6, 17, 0.6, 6, 55.8, 0.2, 0, 0, 0
], ['Eggs', '1 doz.', 32.6, 2.9, 238, 1.0, 52, 18.6, 2.8, 6.5, 1, 0], [
    'Cheese (Cheddar)', '1 lb.', 24.2, 7.4, 448, 16.4, 19, 28.1, 0.8, 10.3,
    4, 0
], ['Cream', '1/2 pt.', 14.1, 3.5, 49, 1.7, 3, 16.9, 0.6, 2.5, 0, 17], [
    'Peanut Butter', '1 lb.', 17.9, 15.7, 661, 1.0, 48, 0, 9.6, 8.1, 471, 0
], ['Mayonnaise', '1/2 pt.', 16.7, 8.6, 18, 0.2, 8, 2.7, 0.4, 0.5, 0, 0], [
    'Crisco', '1 lb.', 20.3, 20.1, 0, 0, 0, 0, 0, 0, 0, 0
], ['Lard', '1 lb.', 9.8, 41.7, 0, 0, 0, 0.2, 0, 0.5, 5, 0], [
    'Sirloin Steak', '1 lb.', 39.6, 2.9, 166, 0.1, 34, 0.2, 2.1, 2.9, 69, 0
], ['Round Steak', '1 lb.', 36.4, 2.2, 214, 0.1, 32, 0.4, 2.5, 2.4, 87, 0
   ], ['Rib Roast', '1 lb.', 29.2, 3.4, 213, 0.1, 33, 0, 0, 2, 0, 0], [
       'Chuck Roast', '1 lb.', 22.6, 3.6, 309, 0.2, 46, 0.4, 1, 4, 120, 0
   ], ['Plate', '1 lb.', 14.6, 8.5, 404, 0.2, 62, 0, 0.9, 0, 0, 0], [
       'Liver (Beef)', '1 lb.', 26.8, 2.2, 333, 0.2, 139, 169.2, 6.4, 50.8,
       316, 525
   ], [
       'Leg of Lamb', '1 lb.', 27.6, 3.1, 245, 0.1, 20, 0, 2.8, 3.9, 86, 0
   ], [
       'Lamb Chops (Rib)',
       '1 lb.', 36.6, 3.3, 140, 0.1, 15, 0, 1.7, 2.7, 54, 0
   ], [
       'Pork Chops', '1 lb.', 30.7, 3.5, 196, 0.2, 30, 0, 17.4, 2.7, 60, 0
   ], [
       'Pork Loin Roast',
       '1 lb.', 24.2, 4.4, 249, 0.3, 37, 0, 18.2, 3.6, 79, 0
   ], ['Bacon', '1 lb.', 25.6, 10.4, 152, 0.2, 23, 0, 1.8, 1.8, 71, 0], [
       'Ham, smoked', '1 lb.', 27.4, 6.7, 212, 0.2, 31, 0, 9.9, 3.3, 50, 0
   ], ['Salt Pork', '1 lb.', 16, 18.8, 164, 0.1, 26, 0, 1.4, 1.8, 0, 0], [
       'Roasting Chicken', '1 lb.', 30.3, 1.8, 184, 0.1, 30, 0.1, 0.9, 1.8,
       68, 46
   ], [
       'Veal Cutlets', '1 lb.', 42.3, 1.7, 156, 0.1, 24, 0, 1.4, 2.4, 57, 0
   ], [
       'Salmon, Pink (can)', '16 oz.', 13, 5.8, 705, 6.8, 45, 3.5,
       1, 4.9, 209, 0
   ], ['Apples', '1 lb.', 4.4, 5.8, 27, 0.5, 36, 7.3, 3.6, 2.7, 5, 544], [
       'Bananas', '1 lb.', 6.1, 4.9, 60, 0.4, 30, 17.4, 2.5, 3.5, 28, 498
   ], ['Lemons', '1 doz.', 26, 1.0, 21, 0.5, 14, 0, 0.5, 0, 4, 952], [
       'Oranges', '1 doz.', 30.9, 2.2, 40, 1.1, 18, 11.1, 3.6, 1.3, 10, 1998
   ], [
       'Green Beans', '1 lb.', 7.1, 2.4, 138, 3.7, 80, 69, 4.3, 5.8, 37, 862
   ], ['Cabbage', '1 lb.', 3.7, 2.6, 125, 4.0, 36, 7.2, 9, 4.5, 26, 5369], [
       'Carrots', '1 bunch', 4.7, 2.7, 73, 2.8, 43, 188.5, 6.1, 4.3, 89, 608
   ], ['Celery', '1 stalk', 7.3, 0.9, 51, 3.0, 23, 0.9, 1.4, 1.4, 9, 313], [
       'Lettuce', '1 head', 8.2, 0.4, 27, 1.1, 22, 112.4, 1.8, 3.4, 11, 449
   ], ['Onions', '1 lb.', 3.6, 5.8, 166, 3.8, 59, 16.6, 4.7, 5.9, 21,
       1184], [
           'Potatoes', '15 lb.', 34, 14.3, 336, 1.8, 118, 6.7, 29.4, 7.1,
           198, 2522
       ], [
           'Spinach', '1 lb.', 8.1, 1.1, 106, 0, 138, 918.4, 5.7, 13.8, 33,
           2755
       ], [
           'Sweet Potatoes', '1 lb.', 5.1, 9.6, 138, 2.7, 54, 290.7, 8.4,
           5.4, 83, 1912
       ], [
           'Peaches (can)', 'No. 2 1/2', 16.8, 3.7, 20, 0.4, 10, 21.5, 0.5,
           1, 31, 196
       ], [
           'Pears (can)', 'No. 2 1/2', 20.4, 3.0, 8, 0.3, 8, 0.8, 0.8, 0.8,
           5, 81
       ], [
           'Pineapple (can)', 'No. 2 1/2', 21.3, 2.4, 16, 0.4, 8, 2, 2.8,
           0.8, 7, 399
       ], [
           'Asparagus (can)', 'No. 2', 27.7, 0.4, 33, 0.3, 12, 16.3, 1.4,
           2.1, 17, 272
       ], [
           'Green Beans (can)', 'No. 2', 10, 1.0, 54, 2, 65, 53.9, 1.6, 4.3,
           32, 431
       ], [
           'Pork and Beans (can)', '16 oz.', 7.1, 7.5, 364, 4, 134, 3.5,
           8.3, 7.7, 56, 0
       ], [
           'Corn (can)', 'No. 2', 10.4, 5.2, 136, 0.2, 16, 12, 1.6, 2.7, 42,
           218
       ], [
           'Peas (can)', 'No. 2', 13.8, 2.3, 136, 0.6, 45, 34.9, 4.9, 2.5,
           37, 370
       ], [
           'Tomatoes (can)', 'No. 2', 8.6, 1.3, 63, 0.7, 38, 53.2, 3.4, 2.5,
           36, 1253
       ], [
           'Tomato Soup (can)', '10 1/2 oz.', 7.6, 1.6, 71, 0.6, 43, 57.9,
           3.5, 2.4, 67, 862
       ], [
           'Peaches, Dried', '1 lb.', 15.7, 8.5, 87, 1.7, 173, 86.8, 1.2,
           4.3, 55, 57
       ], [
           'Prunes, Dried', '1 lb.', 9, 12.8, 99, 2.5, 154, 85.7, 3.9, 4.3,
           65, 257
       ], [
           'Raisins, Dried', '15 oz.', 9.4, 13.5, 104, 2.5, 136, 4.5, 6.3,
           1.4, 24, 136
       ], [
           'Peas, Dried', '1 lb.', 7.9, 20.0, 1367, 4.2, 345, 2.9, 28.7,
           18.4, 162, 0
       ], [
           'Lima Beans, Dried', '1 lb.', 8.9, 17.4, 1055, 3.7, 459, 5.1,
           26.9, 38.2, 93, 0
       ], [
           'Navy Beans, Dried', '1 lb.', 5.9, 26.9, 1691, 11.4, 792, 0,
           38.4, 24.6, 217, 0
       ], ['Coffee', '1 lb.', 22.4, 0, 0, 0, 0, 0, 4, 5.1, 50,
           0], ['Tea', '1/4 lb.', 17.4, 0, 0, 0, 0, 0, 0, 2.3, 42, 0],
        ['Cocoa', '8 oz.', 8.6, 8.7, 237, 3, 72, 0, 2, 11.9, 40, 0], [
            'Chocolate', '8 oz.', 16.2, 8.0, 77, 1.3, 39, 0, 0.9, 3.4, 14, 0
        ], ['Sugar', '10 lb.', 51.7, 34.9, 0, 0, 0, 0, 0, 0, 0, 0],
        ['Corn Syrup', '24 oz.', 13.7, 14.7, 0, 0.5, 74, 0, 0, 0, 5, 0], [
            'Molasses', '18 oz.', 13.6, 9.0, 0, 10.3, 244, 0, 1.9, 7.5, 146,
            0
        ], [
            'Strawberry Preserves', '1 lb.', 20.5, 6.4, 11, 0.4, 7, 0.2,
            0.2, 0.4, 3, 0
        ]]


# In[ ]:


# Calories are set to 3 instead of 3000, because in the table from 1939 Stigler gave the data in 1000s of Calories 
# (see https://math.berkeley.edu/~mgu/MA170F2015/Diet.pdf)
# The notion of `kcal` () taken from the Google example) seems wrong here. 1 Calorie refers to 1000 kcal, not 1 kcal.

print("Nutritional Contraints Table")
display(pd.DataFrame(nutrients, columns = ['Nutrient', 'Daily Recommended Intake']).set_index('Nutrient'))


# In[ ]:


print("Food Nutrition Table")
display(pd.DataFrame(data,columns = ["Commodity","Unit","1939 price (cents)","Calories","Protein (g)","Calcium (g)","Iron (mg)","Vitamin A (IU)","Thiamine (mg)","Riboflavin (mg)","Niacin (mg)","Ascorbic Acid (mg)"]).set_index("Commodity"))


# In[ ]:


# fiddle with nutrients

nutrients = [['Calories (kcal)', 0], ['Protein (g)', 70], [
    'Calcium (g)', 0.8
], ['Iron (mg)', 12], ['Vitamin A (KIU)', 5], ['Vitamin B1 (mg)', 1.8],
             ['Vitamin B2 (mg)', 2.7], ['Niacin (mg)',
                                        18], ['Vitamin C (mg)', 75]]


# In[ ]:


# new data table from https://github.com/google/or-tools/blob/82750ac12f1ee5354e1c7869894d9af3508778f2/examples/contrib/stigler_contrib.py
#
# removed coffee and tea from the list as they had 0 Calories

commodities = [["Wheat Flour (Enriched)", "10 lb."], ["Macaroni", "1 lb."],
                 ["Wheat Cereal (Enriched)",
                  "28 oz."], ["Corn Flakes", "8 oz."], ["Corn Meal", "1 lb."],
                 ["Hominy Grits", "24 oz."], ["Rice", "1 lb."],
                 ["Rolled Oats", "1 lb."], ["White Bread (Enriched)", "1 lb."],
                 ["Whole Wheat Bread", "1 lb."], ["Rye Bread", "1 lb."],
                 ["Pound Cake", "1 lb."], ["Soda Crackers", "1 lb."],
                 ["Milk", "1 qt."], ["Evaporated Milk (can)", "14.5 oz."],
                 ["Butter", "1 lb."], ["Oleomargarine", "1 lb."],
                 ["Eggs", "1 doz."], ["Cheese (Cheddar)", "1 lb."],
                 ["Cream", "1/2 pt."], ["Peanut Butter", "1 lb."],
                 ["Mayonnaise", "1/2 pt."], ["Crisco", "1 lb."],
                 ["Lard", "1 lb."], ["Sirloin Steak", "1 lb."],
                 ["Round Steak", "1 lb."], ["Rib Roast", "1 lb."],
                 ["Chuck Roast", "1 lb."], ["Plate", "1 lb."],
                 ["Liver (Beef)", "1 lb."], ["Leg of Lamb", "1 lb."],
                 ["Lamb Chops (Rib)", "1 lb."], ["Pork Chops", "1 lb."],
                 ["Pork Loin Roast", "1 lb."], ["Bacon", "1 lb."],
                 ["Ham - smoked", "1 lb."], ["Salt Pork", "1 lb."],
                 ["Roasting Chicken", "1 lb."], ["Veal Cutlets", "1 lb."],
                 ["Salmon, Pink (can)", "16 oz."], ["Apples", "1 lb."],
                 ["Bananas", "1 lb."], ["Lemons", "1 doz."],
                 ["Oranges", "1 doz."], ["Green Beans", "1 lb."],
                 ["Cabbage", "1 lb."], ["Carrots", "1 bunch"],
                 ["Celery", "1 stalk"], ["Lettuce", "1 head"],
                 ["Onions", "1 lb."], ["Potatoes", "15 lb."],
                 ["Spinach", "1 lb."], ["Sweet Potatoes", "1 lb."],
                 ["Peaches (can)", "No. 2 1/2"], ["Pears (can)", "No. 2 1/2,"],
                 ["Pineapple (can)", "No. 2 1/2"], ["Asparagus (can)", "No. 2"],
                 ["Grean Beans (can)", "No. 2"],
                 ["Pork and Beans (can)", "16 oz."], ["Corn (can)", "No. 2"],
                 ["Peas (can)", "No. 2"], ["Tomatoes (can)", "No. 2"],
                 ["Tomato Soup (can)", "10 1/2 oz."],
                 ["Peaches, Dried", "1 lb."], ["Prunes, Dried", "1 lb."],
                 ["Raisins, Dried", "15 oz."], ["Peas, Dried", "1 lb."],
                 ["Lima Beans, Dried", "1 lb."], ["Navy Beans, Dried", "1 lb."],
                 ["Coffee", "1 lb."], ["Tea", "1/4 lb."], ["Cocoa", "8 oz."],
                 ["Chocolate", "8 oz."], ["Sugar", "10 lb."],
                 ["Corn Sirup", "24 oz."], ["Molasses", "18 oz."],
                 ["Strawberry Preserve", "1 lb."]]

# price and weight are the two first columns
data = [
  [36.0, 12600.0, 44.7, 1411.0, 2.0, 365.0, 0.0, 55.4, 33.3, 441.0, 0.0],
  [14.1, 3217.0, 11.6, 418.0, 0.7, 54.0, 0.0, 3.2, 1.9, 68.0, 0.0],
  [24.2, 3280.0, 11.8, 377.0, 14.4, 175.0, 0.0, 14.4, 8.8, 114.0, 0.0],
  [7.1, 3194.0, 11.4, 252.0, 0.1, 56.0, 0.0, 13.5, 2.3, 68.0, 0.0],
  [4.6, 9861.0, 36.0, 897.0, 1.7, 99.0, 30.9, 17.4, 7.9, 106.0, 0.0],
  [8.5, 8005.0, 28.6, 680.0, 0.8, 80.0, 0.0, 10.6, 1.6, 110.0, 0.0],
  [7.5, 6048.0, 21.2, 460.0, 0.6, 41.0, 0.0, 2.0, 4.8, 60.0, 0.0],
  [7.1, 6389.0, 25.3, 907.0, 5.1, 341.0, 0.0, 37.1, 8.9, 64.0, 0.0],
  [7.9, 5742.0, 15.6, 488.0, 2.5, 115.0, 0.0, 13.8, 8.5, 126.0, 0.0],
  [9.1, 4985.0, 12.2, 484.0, 2.7, 125.0, 0.0, 13.9, 6.4, 160.0, 0.0],
  [9.2, 4930.0, 12.4, 439.0, 1.1, 82.0, 0.0, 9.9, 3.0, 66.0, 0.0],
  [24.8, 1829.0, 8.0, 130.0, 0.4, 31.0, 18.9, 2.8, 3.0, 17.0, 0.0],
  [15.1, 3004.0, 12.5, 288.0, 0.5, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [11.0, 8867.0, 6.1, 310.0, 10.5, 18.0, 16.8, 4.0, 16.0, 7.0, 177.0],
  [6.7, 6035.0, 8.4, 422.0, 15.1, 9.0, 26.0, 3.0, 23.5, 11.0, 60.0],
  [20.8, 1473.0, 10.8, 9.0, 0.2, 3.0, 44.2, 0.0, 0.2, 2.0, 0.0],
  [16.1, 2817.0, 20.6, 17.0, 0.6, 6.0, 55.8, 0.2, 0.0, 0.0, 0.0],
  [32.6, 1857.0, 2.9, 238.0, 1.0, 52.0, 18.6, 2.8, 6.5, 1.0, 0.0],
  [24.2, 1874.0, 7.4, 448.0, 16.4, 19.0, 28.1, 0.8, 10.3, 4.0, 0.0],
  [14.1, 1689.0, 3.5, 49.0, 1.7, 3.0, 16.9, 0.6, 2.5, 0.0, 17.0],
  [17.9, 2534.0, 15.7, 661.0, 1.0, 48.0, 0.0, 9.6, 8.1, 471.0, 0.0],
  [16.7, 1198.0, 8.6, 18.0, 0.2, 8.0, 2.7, 0.4, 0.5, 0.0, 0.0],
  [20.3, 2234.0, 20.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [9.8, 4628.0, 41.7, 0.0, 0.0, 0.0, 0.2, 0.0, 0.5, 5.0, 0.0],
  [39.6, 1145.0, 2.9, 166.0, 0.1, 34.0, 0.2, 2.1, 2.9, 69.0, 0.0],
  [36.4, 1246.0, 2.2, 214.0, 0.1, 32.0, 0.4, 2.5, 2.4, 87.0, 0.0],
  [29.2, 1553.0, 3.4, 213.0, 0.1, 33.0, 0.0, 0.0, 2.0, 0.0, 0.0],
  [22.6, 2007.0, 3.6, 309.0, 0.2, 46.0, 0.4, 1.0, 4.0, 120.0, 0.0],
  [14.6, 3107.0, 8.5, 404.0, 0.2, 62.0, 0.0, 0.9, 0.0, 0.0, 0.0],
  [26.8, 1692.0, 2.2, 333.0, 0.2, 139.0, 169.2, 6.4, 50.8, 316.0, 525.0],
  [27.6, 1643.0, 3.1, 245.0, 0.1, 20.0, 0.0, 2.8, 3.0, 86.0, 0.0],
  [36.6, 1239.0, 3.3, 140.0, 0.1, 15.0, 0.0, 1.7, 2.7, 54.0, 0.0],
  [30.7, 1477.0, 3.5, 196.0, 0.2, 80.0, 0.0, 17.4, 2.7, 60.0, 0.0],
  [24.2, 1874.0, 4.4, 249.0, 0.3, 37.0, 0.0, 18.2, 3.6, 79.0, 0.0],
  [25.6, 1772.0, 10.4, 152.0, 0.2, 23.0, 0.0, 1.8, 1.8, 71.0, 0.0],
  [27.4, 1655.0, 6.7, 212.0, 0.2, 31.0, 0.0, 9.9, 3.3, 50.0, 0.0],
  [16.0, 2835.0, 18.8, 164.0, 0.1, 26.0, 0.0, 1.4, 1.8, 0.0, 0.0],
  [30.3, 1497.0, 1.8, 184.0, 0.1, 30.0, 0.1, 0.9, 1.8, 68.0, 46.0],
  [42.3, 1072.0, 1.7, 156.0, 0.1, 24.0, 0.0, 1.4, 2.4, 57.0, 0.0],
  [13.0, 3489.0, 5.8, 705.0, 6.8, 45.0, 3.5, 1.0, 4.9, 209.0, 0.0],
  [4.4, 9072.0, 5.8, 27.0, 0.5, 36.0, 7.3, 3.6, 2.7, 5.0, 544.0],
  [6.1, 4982.0, 4.9, 60.0, 0.4, 30.0, 17.4, 2.5, 3.5, 28.0, 498.0],
  [26.0, 2380.0, 1.0, 21.0, 0.5, 14.0, 0.0, 0.5, 0.0, 4.0, 952.0],
  [30.9, 4439.0, 2.2, 40.0, 1.1, 18.0, 11.1, 3.6, 1.3, 10.0, 1993.0],
  [7.1, 5750.0, 2.4, 138.0, 3.7, 80.0, 69.0, 4.3, 5.8, 37.0, 862.0],
  [3.7, 8949.0, 2.6, 125.0, 4.0, 36.0, 7.2, 9.0, 4.5, 26.0, 5369.0],
  [4.7, 6080.0, 2.7, 73.0, 2.8, 43.0, 188.5, 6.1, 4.3, 89.0, 608.0],
  [7.3, 3915.0, 0.9, 51.0, 3.0, 23.0, 0.9, 1.4, 1.4, 9.0, 313.0],
  [8.2, 2247.0, 0.4, 27.0, 1.1, 22.0, 112.4, 1.8, 3.4, 11.0, 449.0],
  [3.6, 11844.0, 5.8, 166.0, 3.8, 59.0, 16.6, 4.7, 5.9, 21.0, 1184.0],
  [34.0, 16810.0, 14.3, 336.0, 1.8, 118.0, 6.7, 29.4, 7.1, 198.0, 2522.0],
  [8.1, 4592.0, 1.1, 106.0, 0.0, 138.0, 918.4, 5.7, 13.8, 33.0, 2755.0],
  [5.1, 7649.0, 9.6, 138.0, 2.7, 54.0, 290.7, 8.4, 5.4, 83.0, 1912.0],
  [16.8, 4894.0, 3.7, 20.0, 0.4, 10.0, 21.5, 0.5, 1.0, 31.0, 196.0],
  [20.4, 4030.0, 3.0, 8.0, 0.3, 8.0, 0.8, 0.8, 0.8, 5.0, 81.0],
  [21.3, 3993.0, 2.4, 16.0, 0.4, 8.0, 2.0, 2.8, 0.8, 7.0, 399.0],
  [27.7, 1945.0, 0.4, 33.0, 0.3, 12.0, 16.3, 1.4, 2.1, 17.0, 272.0],
  [10.0, 5386.0, 1.0, 54.0, 2.0, 65.0, 53.9, 1.6, 4.3, 32.0, 431.0],
  [7.1, 6389.0, 7.5, 364.0, 4.0, 134.0, 3.5, 8.3, 7.7, 56.0, 0.0],
  [10.4, 5452.0, 5.2, 136.0, 0.2, 16.0, 12.0, 1.6, 2.7, 42.0, 218.0],
  [13.8, 4109.0, 2.3, 136.0, 0.6, 45.0, 34.9, 4.9, 2.5, 37.0, 370.0],
  [8.6, 6263.0, 1.3, 63.0, 0.7, 38.0, 53.2, 3.4, 2.5, 36.0, 1253.0],
  [7.6, 3917.0, 1.6, 71.0, 0.6, 43.0, 57.9, 3.5, 2.4, 67.0, 862.0],
  [15.7, 2889.0, 8.5, 87.0, 1.7, 173.0, 86.8, 1.2, 4.3, 55.0, 57.0],
  [9.0, 4284.0, 12.8, 99.0, 2.5, 154.0, 85.7, 3.9, 4.3, 65.0, 257.0],
  [9.4, 4524.0, 13.5, 104.0, 2.5, 136.0, 4.5, 6.3, 1.4, 24.0, 136.0],
  [7.9, 5742.0, 20.0, 1367.0, 4.2, 345.0, 2.9, 28.7, 18.4, 162.0, 0.0],
  [8.9, 5097.0, 17.4, 1055.0, 3.7, 459.0, 5.1, 26.9, 38.2, 93.0, 0.0],
  [5.9, 7688.0, 26.9, 1691.0, 11.4, 792.0, 0.0, 38.4, 24.6, 217.0, 0.0],
  [22.4, 2025.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.1, 50.0, 0.0],
  [17.4, 652.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.3, 42.0, 0.0],
  [8.6, 2637.0, 8.7, 237.0, 3.0, 72.0, 0.0, 2.0, 11.9, 40.0, 0.0],
  [16.2, 1400.0, 8.0, 77.0, 1.3, 39.0, 0.0, 0.9, 3.4, 14.0, 0.0],
  [51.7, 8773.0, 34.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [13.7, 4996.0, 14.7, 0.0, 0.5, 74.0, 0.0, 0.0, 0.0, 5.0, 0.0],
  [13.6, 3752.0, 9.0, 0.0, 10.3, 244.0, 0.0, 1.9, 7.5, 146.0, 0.0],
  [20.5, 2213.0, 6.4, 11.0, 0.4, 7.0, 0.2, 0.2, 0.4, 3.0, 0.0]
]


# In[ ]:


solver = pywraplp.Solver.CreateSolver('GLOP')


# In[ ]:


# Declare an array to hold our variables. 
foods = [solver.NumVar(0.0, solver.infinity(), item[0]) for item in commodities]

print('Number of variables =', solver.NumVariables())


# In[ ]:


# Create the constraints, one per nutrient. (data = nutrients_per_dollar)
# gurobipy can express a lists or arrays of constraints with a nicer DSL 
# instead of the many loops necessary with OR-Tools
constraints = []
for i, nutrient in enumerate(nutrients):
    constraints.append(solver.Constraint(nutrient[1], solver.infinity()))
    for j, item in enumerate(data):
        constraints[i].SetCoefficient(foods[j], item[i + 2])

print('Number of constraints =', solver.NumConstraints())


# In[ ]:


# Objective function: Minimize the sum of (price-normalized) foods.
objective = solver.Objective()
for i, food in enumerate(foods):
    objective.SetCoefficient(food, data[i][1])
objective.SetMinimization()


# In[ ]:


status = solver.Solve()

# Check that the problem has an optimal solution.
if status != solver.OPTIMAL:
    print('The problem does not have an optimal solution!')
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')
        exit(1)


# In[ ]:


# Display the amounts (in dollars) to purchase of each food.
nutrients_result = [0] * len(nutrients)
print('\nDaily Foods:')
for i, food in enumerate(foods):
    if food.solution_value() > 0.0:
        print('{}: ${} {} gr'.format(commodities[i][0], food.solution_value(), food.solution_value() * data[i][1]))
        for j, _ in enumerate(nutrients):
            nutrients_result[j] += data[i][j + 2] * food.solution_value()
print('\nOptimal daily weight: {:.4f} gr'.format(objective.Value()))


# In[ ]:


print('\nNutrients per day:')
for i, nutrient in enumerate(nutrients):
    print('{}: {:.2f} (min {})'.format(nutrient[0], nutrients_result[i],
                                       nutrient[1]))


# ## Stieglers diet remarks
# 
# > "No one recommends these diets for anyone, let alone everyone." (Stigler)
# 
# My observation: The amount of iron for spinach is 10x as high as in reality. Fixing this does not change the result. So why is spinach included in the diet? 
# 

# In[ ]:


nutrient_per_food = {}

for i, food in enumerate(foods):
    if food.solution_value() > 0.0:      
        for j, nutrient in enumerate(nutrients):
            if food in nutrient_per_food:
                nutrient_per_food[food].append(data[i][j + 2] * food.solution_value())
            else:
                nutrient_per_food[food]=[data[i][j + 2] * food.solution_value()]
                
foods_df = pd.DataFrame.from_dict(nutrient_per_food, orient='index', columns=[n[0] for n in nutrients])

for i, nutrient in enumerate(nutrients):
    foods_df[nutrient[0]]=(foods_df[nutrient[0]]/nutrients_result[i]*100).round(2)

display(foods_df)                 


# ## The end
# 
# Google OR-Tools seem the best free open-source tool for solving OR problems:
# - good documentation
# - many examples
# - gurobipy has a nicer DSL for defining lists/arrays of constraints
# - gurobipy free trial is limited to 2000 variables, OR-Tools are unlimited
# 
# **Next session**: How to solve the facility location problem with OR-Tools and apply that to solve the Shell Hackathon.
# 
# <span style="font-size:larger;">Eat your spinach - Not for the iron, but for the Vitamin A!</span>
