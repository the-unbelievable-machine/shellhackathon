#!/usr/bin/env python
# coding: utf-8

# # Simplified Shell Hackathon problem
# 
# How many parking slots with chargers installed as in 2018 do we need to open to fulfill electricity demand of 2018?
# 
# This is a capacitated FLP completely analogeous to our example 2, except parking slot/facility capacities vary.

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
fast_charger = 400


# In[ ]:


setup_cost = 1
# assume fixed capacities of parking slots 
capacities = (supply["existing_num_SCS"]*slow_charger + supply["existing_num_FCS"]*fast_charger).tolist()
demands = demand["2018"].tolist()


# In[ ]:


sum(capacities) > sum(demands), sum(capacities), sum(demands)


# The total capacity is suspiciously close to total demand. Are the numbers of shell hackathon problem generated artificially? This suggest that we definitely need all parking slots opened.

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


solver = pywraplp.Solver.CreateSolver('SCIP_MIXED_INTEGER_PROGRAMMING')


# In[ ]:


# Variables
select = {}
for j in range(num_facilities):
    select[j] = solver.BoolVar("Select")
assign = {}
for i,j in distance.keys(): 
    assign[(i,j)] = solver.NumVar(0,solver.infinity(),"Assign")    


# In[ ]:


# demand constraints
for i in range(num_customers):
    solver.Add(sum(assign[(i,j)] for j in range(num_facilities)) == demands[i] )
# shipping constraints
for i,j in distance.keys():
    solver.Add(assign[(i,j)] <= select[j]*demands[i])
# capacity constraints
for j in range(num_facilities):
    solver.Add(sum(assign[(i,j)] for i in range(num_customers)) <= select[j]*capacities[j])    


# In[ ]:


objective = solver.Objective()
# parking slot opening costs
for j in range(num_facilities):
    objective.SetCoefficient(select[j], setup_cost)
# distance costs       
for i in range(num_customers):
    for j in range(num_facilities):
        objective.SetCoefficient(assign[(i,j)],distance[(i,j)])
objective.SetMinimization()        


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
for facility in select.keys():
    if (abs(select[facility].solution_value()) > 1e-6):
        lines.append(f"Open a parking lot at location {facility + 1}.")
for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)
    
print("Number of parking slots open:", len(lines))    


# In[ ]:


# Shipments from facilities to customers.
lines = []
for customer, facility in assign.keys():
    if (abs(assign[customer, facility].solution_value()) > 1e-6):
        lines.append(f"Demand point {customer + 1} receives {round(assign[customer, facility].solution_value(), 2)} of its demand {demands[customer]} from parking slot {facility + 1} .")
for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)


# In[ ]:




