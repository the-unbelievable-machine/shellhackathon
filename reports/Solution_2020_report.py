#!/usr/bin/env python
# coding: utf-8

# # Shell Hackathon Solution 2020
# 
# This is the same code as for the solution for 2019, except that we use the predicted electricity demand of 2020 as input. And we use the infrastructure suggested by our solution from 2019 as basis for computing the optimal solution for 2020.

# In[ ]:


from math import sqrt
from itertools import product

import pandas as pd

from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit


# In[ ]:


supply = pd.read_csv("../data/processed/exisiting_EV_infrastructure_2019.csv")
demand = pd.read_csv("../data/processed/Demand_Future.csv")


# In[ ]:


slow_charger = 200
slow_costs = 1.0*600
fast_charger = 400
fast_costs = 1.5*600


# In[ ]:


# real capacities
real_capacities = (supply["existing_num_SCS"]*slow_charger + supply["existing_num_FCS"]*fast_charger).tolist()
# maximum theoretical capacities
capacities = (supply["total_parking_slots"]*fast_charger).tolist()
demands = demand["2020"].tolist()


# In[ ]:


sum(capacities) > sum(demands), sum(capacities), sum(demands), sum(real_capacities)


# Also for 2020 the maximal capacity of all parking slots is enough to fulfill the demand.

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
#for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)
    
print("Number of construction sites:", len(lines))          


# In[ ]:


# compute the total electricity supply of our solution
total_supply = 0
for j in range(num_facilities):
    total_supply += slow[j].solution_value()*200 + fast[j].solution_value()*400
sum(demands), total_supply   


# In 2020 our total supply is closer to the predicted demand than in 2018 and 2019.

# In[ ]:


# Shipments from facilities to customers.
lines = []
for i, j in assign.keys():
    if (abs(assign[i, j].solution_value()) > 1e-6):
        lines.append(f"Demand point {i + 1} receives {round(assign[i, j].solution_value(), 2)} of its demand {round(demands[i],2)} from parking slot {j + 1} .")
for line in lines[:5]: print(line)
print("...")
for line in lines[-5:]: print(line)   


# ### Creating result file for submission
# 
# This file will later be used to create the final submission.

# In[ ]:


slow_list = []
for j in range(num_facilities):
    slow_list.append((2020, "SCS", "", j, slow[j].solution_value()))
fast_list = []
for j in range(num_facilities):
    fast_list.append((2020, "FCS", "", j, fast[j].solution_value()))    


# In[ ]:


assign_list = []
for i in range(num_customers):
    for j in range(num_facilities):
        assign_list.append((2020, "DS", i, j, assign[(i,j)].solution_value()))


# In[ ]:


result = slow_list + fast_list + assign_list


# In[ ]:


df_result = pd.DataFrame(result, columns=["year", "data_type", "demand_point_index", "supply_point_index", "value"])
df_result


# In[ ]:


# commented out, so we don't overwrite the result
# df_result.to_csv("../data/processed/result_2020.csv")


# In[ ]:


# commented out, so we don't overwrite the result
# supply_2020.to_csv("../data/processed/exisiting_EV_infrastructure_2020.csv")


# ### Fiddeling with numerical issues
# 
# Here we show, that truncating the numerical values of our solution will make sure that constraint 5 is never violated. It should be noted, that rounding doesn't work for this.

# In[ ]:


# Simple rounding leads to violations of the constraint
violations = []
for j in range(num_facilities):
    constraint = sum(round(assign[(i,j)].solution_value(),2) for i in range(num_customers))<= (slow[j].solution_value()*200 + fast[j].solution_value()*400)
    if not constraint:
        violations.append(constraint)
len(violations)


# In[ ]:


# We need to truncate the results. Otherwise the constraints are violated due to floating point issues
# see https://stackoverflow.com/a/49960574
def truncate(theNumber, theDigits):
    myDigits = 10 ** theDigits
    return (int(theNumber * myDigits) / myDigits)


# In[ ]:


violations = []
for j in range(num_facilities):
    constraint = sum(truncate(assign[(i,j)].solution_value(),2) for i in range(num_customers))<= (slow[j].solution_value()*200 + fast[j].solution_value()*400)
    if not constraint:
        violations.append(constraint)
len(violations)        

