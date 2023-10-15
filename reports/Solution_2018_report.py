#!/usr/bin/env python
# coding: utf-8

# # Shell Hackathon Solution 2018
# 
# We know that the total capacity of the installed charger in 2018 meets the demand of 2018 nearly exactly. So the optimal number of chargers to be build should be zero.

# In[ ]:


from math import sqrt
from itertools import product

import pandas as pd

from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit


# In[ ]:


supply = pd.read_csv("../data/raw/exisiting_EV_infrastructure_2018.csv")
demand = pd.read_csv("../data/raw/Demand_History.csv")


# In[ ]:


slow_charger = 200
slow_costs = 1.0*600
fast_charger = 400
fast_costs = 1.5*600


# A fast charger delivers twice the capacity but cost only 1.5 times the amount of a slow charger. Building fast chargers is therefor optimal.

# In[ ]:


# real capacities
real_capacities = (supply["existing_num_SCS"]*slow_charger + supply["existing_num_FCS"]*fast_charger).tolist()
# maximum theoretical capacities
capacities = (supply["total_parking_slots"]*fast_charger).tolist()
demands = demand["2018"].tolist()


# In[ ]:


sum(capacities) > sum(demands), sum(capacities), sum(demands), sum(real_capacities)


# The maximal capacity of all parking slots is more than enough to fulfill the demand.

# In[ ]:


# facilities are parking slots
facilities = list(supply[["x_coordinate","y_coordinate"]].itertuples(index=False, name=None))
# customers are areas of electricity demand
customers = list(demand[["x_coordinate","y_coordinate"]].itertuples(index=False, name=None))


# In[ ]:


# Compute key parameters of MIP model formulation
num_facilities = len(facilities)
num_customers = len(customers)
cartesian_prod = list(product(range(num_customers), range(num_facilities)))


# In[ ]:


# This function determines the Euclidean distance between a facility and customer sites.
def compute_distance(loc1, loc2):
    dx = loc1[0] - loc2[0]
    dy = loc1[1] - loc2[1]
    return sqrt(dx*dx + dy*dy)


# In[ ]:


# Compute distance matrix
distance = {(c,f): compute_distance(customers[c], facilities[f]) for c, f in cartesian_prod}


# In[ ]:


# maximum slots for chargers
slots = supply["total_parking_slots"].tolist()

# existing chargers
slow_slots = supply["existing_num_SCS"].tolist()
fast_slots = supply["existing_num_FCS"].tolist()


# In[ ]:


## For testing set number of slots to zero
# slow_slots = [0]*len(facilities)
# fast_slots = [0]*len(facilities)


# In[ ]:


solver = pywraplp.Solver.CreateSolver('SCIP_MIXED_INTEGER_PROGRAMMING')


# In[ ]:


# Variables
assign = {}
for i,j in distance.keys(): 
    assign[(i,j)] = solver.NumVar(0,solver.infinity(),"Assign")
# Do not delete existing chargers (Constraint/Boundaries 2) 
slow = {}
for j in range(num_facilities):
    slow[j] = solver.IntVar(slow_slots[j], solver.infinity(), "Slow")
fast = {}
for j in range(num_facilities):
    fast[j] = solver.IntVar(fast_slots[j], solver.infinity(), "Fast")          


# In[ ]:


# Constraint 3 (slots)
for j in range(num_facilities):
    solver.Add(slow[j] + fast[j] <= slots[j])
# Constraint 5 (capacity constraints)
for j in range(num_facilities):
    solver.Add(sum(assign[(i,j)] for i in range(num_customers)) <= (slow[j]*200 + fast[j]*400))
# Constraint 6 (demand constraints)
for i in range(num_customers):
    solver.Add(sum(assign[(i,j)] for j in range(num_facilities)) == demands[i] )    


# In[ ]:


objective = solver.Objective()
# Building costs for chargers
for j in range(num_facilities):
    objective.SetCoefficient(slow[j], slow_costs)
for j in range(num_facilities):
    objective.SetCoefficient(fast[j], fast_costs)
# distance costs
for i in range(num_customers):
    for j in range(num_facilities):
        objective.SetCoefficient(assign[(i,j)],distance[(i,j)]) 
objective.SetMinimization()    


# The Shell Hackathon cost function includes the MAE of the demand prediction as additional term. We know the exact demand for 2018, so this term is zero. For 2019/2020 we cannot compute the term, because we only have the predicted values, but not the exact ones.

# In[ ]:


status = solver.Solve()


# In[ ]:


if status == pywraplp.Solver.OPTIMAL:
    print('Objective value =', solver.Objective().Value())
    print()
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
else:
    print('The problem does not have an optimal solution.')


# In[ ]:


# display optimal values of decision variables
lines = []
for j in range(num_facilities):
    build_slow = slow[j].solution_value() - slow_slots[j]
    build_fast = fast[j].solution_value() - fast_slots[j]
    if build_slow > 0 or build_fast > 0: 
        lines.append(f"Build {slow[j].solution_value() - slow_slots[j]} slow charger  and {fast[j].solution_value() - fast_slots[j]} fast charger at location {j + 1}.")
for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)
    
print("Number of construction sites:", len(lines))          


# Surprisingly we find that according to our solver we should build additional chargers at 24 parking slots.

# In[ ]:


# compute the total electricity supply of our solution
total_supply = 0
for j in range(num_facilities):
    total_supply += slow[j].solution_value()*200 + fast[j].solution_value()*400


# In[ ]:


sum(demands), total_supply 


# Our supply is much bigger that our demand. I don't understand why the solver comes up with that. Maybe this lowers the distance costs?

# In[ ]:


# compute the total demand of our solution
total_demand = 0.0
for i in range(num_customers):
    for j in range(num_facilities):
        total_demand += assign[(i,j)].solution_value()


# In[ ]:


sum(demands), total_demand


# The total demand of our solution is exactly the sum of input demands. So we don't violate that constraint. 

# In[ ]:


# Shipments from facilities to customers.
lines = []
for i, j in assign.keys():
    if (abs(assign[i, j].solution_value()) > 1e-6):
        lines.append(f"Demand point {i + 1} receives {round(assign[i, j].solution_value(), 2)} of its demand {round(demands[i],2)} from parking slot {j + 1} .")
for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)        


# In[ ]:




