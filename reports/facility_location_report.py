#!/usr/bin/env python
# coding: utf-8

# # Facility location problem (FLP)
# 
# Location analysis is a branch of OR
# 
# Fermat-Weber (geometric median) problem (17th century):
# - Find a fourth point so the sum of its (weighted) distances to three given points is minimal 
# 
# FLP: Determine location of new factories based on 
# - transportation distance, costs 
# - facility opening/maintenance cost
# - demand
# - Variation 1: (un-)capacitated FLP: facilities have (un-)limited capcacity
# - Variation 2: fixed locations FLP: choose the best of a number of fixed locations    
#   

# FLP is
# - a mixed integer programming problem 
# - for fixed locations it is a LP problem (Simplex algorithm)
# - if locations are not fixed it needs Second Order Cone Optimization (Interior points algorithm), see [Mathematica/ConvexOptimization/FLP](https://www.wolfram.com/language/12/convex-optimization/facility-location-problem.html)  
# 
# ![Hierarchy of convex optimization](https://upload.wikimedia.org/wikipedia/commons/1/11/Hierarchy_compact_convex.png)
# 
# Fortunately the Shell Hackathon optimization problem is a capacitated, fixed location FLP. 

# ## Example 1 (uncapacitated FLP)
# 
# Given $i$ supermarket coordinates find the optimal location of $j$ warehouses/facilities from a list of possible locations. 
# Many warehouses would reduce the transportation costs $c_{ij}$ to supermarkets, however opening a warehouse generates fixed costs $f_j$.
# 
# Variables:
# - $s_j \in {0,1}$ boolean variable = 1 if warehouse is build
# - $0 \leq a_{ij} \leq 1$ non-negative continuous variable, the fraction of supply received by customer $i$ from warehouse $j$
# 
# Objective:
# $$
# min \left( \sum_j f_j s_j + \sum_j \sum_i c_{ij} a_{ij} \right)
# $$
# 
# 
# See
# - https://www.gurobi.com/resource/modeling-examples-using-the-gurobi-python-api-in-jupyter-notebook/
# - https://www.gurobi.com/resource/facility-location-problem/

# Contraints:
# 1. Demand (the sum of all fractions for a supermarkt $i$ over all warehouses $j$ must be 1)
# $$
# \sum_j a_{ij} = 1
# $$
# 2. Shipping (warehouse $j$ must be opened to allow shipping)
# $$
# a_{ij} \leq s_j
# $$

# In[ ]:


from math import sqrt
from itertools import product

from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit


# In[ ]:


# Parameters
customers = [(0,1.5), (2.5,1.2)]
facilities = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]
setup_cost = [3,2,3,1,3,3,4,3,2]
cost_per_mile = 1


# In[ ]:


# This function determines the Euclidean distance between a facility and customer sites.
def compute_distance(loc1, loc2):
    dx = loc1[0] - loc2[0]
    dy = loc1[1] - loc2[1]
    return sqrt(dx*dx + dy*dy)


# In[ ]:


# Compute key parameters of MIP model formulation
num_facilities = len(facilities)
num_customers = len(customers)
cartesian_prod = list(product(range(num_customers), range(num_facilities)))


# In[ ]:


# Compute shipping costs
shipping_cost = {(c,f): cost_per_mile*compute_distance(customers[c], facilities[f]) for c, f in cartesian_prod}


# In[ ]:


list(shipping_cost.items())[:5]


# In[ ]:


# The COIN-OR Solver crashed 
# solver = pywraplp.Solver.CreateSolver('CBC_MIXED_INTEGER_PROGRAMMING')
# Using SCIP for MIP problem (see https://developers.google.com/optimization/mip/mip_example)
#
# see all possible solvers here: https://google.github.io/or-tools/python/ortools/linear_solver/pywraplp.html
solver = pywraplp.Solver.CreateSolver('SCIP_MIXED_INTEGER_PROGRAMMING')


# In[ ]:


# Variables
select = {}
for j in range(num_facilities):
    select[j] = solver.BoolVar("Select")
assign = {}
for i,j in shipping_cost.keys(): 
    assign[(i,j)] = solver.NumVar(0,1,"Assign")    


# In[ ]:


# demand constraints
for i in range(num_customers):
    solver.Add(sum(assign[(i,j)] for j in range(num_facilities)) == 1)   
# shipping constraints
for i,j in cartesian_prod:
    solver.Add(assign[(i,j)] <= select[j])


# In[ ]:


objective = solver.Objective()
# warehouse opening costs
for j in range(num_facilities):
    objective.SetCoefficient(select[j], setup_cost[j])
# transportation costs    
for i in range(num_customers):
    for j in range(num_facilities):
        objective.SetCoefficient(assign[(i,j)],shipping_cost[(i,j)]) 
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
for facility in select.keys():
    if (abs(select[facility].solution_value()) > 1e-6):
        print(f"\n Build a warehouse at location {facility + 1}.")


# In[ ]:


# Shipments from facilities to customers.
for customer, facility in assign.keys():
    if (abs(assign[customer, facility].solution_value()) > 1e-6):
        print(f"\n Supermarket {customer + 1} receives {round(100*assign[customer, facility].solution_value(), 2)} % of its demand  from Warehouse {facility + 1} .")


# # Example 2 (capacitated FLP)
# 
# In addition to example 1 we now want our supermarkets/customers to have different demands $d_i$ and the warehouses facilities have a fixed limited capacity $c$. The setup costs $f_i$ are assumed to be constant.
# 
# Variables:
# - $s_j \in {0,1}$ boolean variable = 1 if warehouse is build
# - $0 \leq a_{ij} \leq \infty$ non-negative continuous variable, the amount of supply received by customer $i$ from warehouse $j$
# 
# see 
# - https://scipbook.readthedocs.io/en/latest/flp.html

# Contraints:
# 1. Demand (the demand $d_i$ of a supermarket/customer must be equal to the sum of supplies over all warehouses $j$)
# $$
# \sum_j a_{ij} = d_i
# $$
# 2. Shipping (warehouse $j$ must be opened to allow shipping)
# $$
# a_{ij} \leq s_j d_i
# $$
# 3. Capacity constraint (the sum of supplies over all customers $i$ for a open warehouse $j$ must be smaller than the capcaity $c$)
# $$
# \sum_i a_{ij} \leq s_j c
# $$

# In[ ]:


setup_cost = 1000
f_capacity = 500
demands = [80, 270, 250, 160, 180]


# In[ ]:


costs = {}
costs[0] = [4,5,6,8,10]
costs[1] = [6,4,3,5,8]
costs[2] = [9,7,4,3,4]

shipping_cost = {}
for i in range(len(demands)):
    for j in costs.keys():
        shipping_cost[(i,j)]=costs[j][i]


# In[ ]:


solver = pywraplp.Solver.CreateSolver('SCIP_MIXED_INTEGER_PROGRAMMING')


# In[ ]:


num_facilities = len(costs.keys())
num_customers = len(demands)


# In[ ]:


# Variables
select = {}
for j in range(num_facilities):
    select[j] = solver.BoolVar("Select")
assign = {}
for i,j in shipping_cost.keys(): 
    assign[(i,j)] = solver.NumVar(0,solver.infinity(),"Assign")    


# In[ ]:


# demand constraints
for i in range(num_customers):
    solver.Add(sum(assign[(i,j)] for j in range(num_facilities)) == demands[i] )
# shipping constraints
for i,j in shipping_cost.keys():
    solver.Add(assign[(i,j)] <= select[j]*demands[i])
# capacity constraints
for j in range(num_facilities):
    solver.Add(sum(assign[(i,j)] for i in range(num_customers)) <= select[j]*f_capacity)    


# In[ ]:


objective = solver.Objective()
# warehouse opening costs
for j in range(num_facilities):
    objective.SetCoefficient(select[j], setup_cost)
# transportation costs    
for i in range(num_customers):
    for j in range(num_facilities):
        objective.SetCoefficient(assign[(i,j)],shipping_cost[(i,j)]) 
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
for facility in select.keys():
    if (abs(select[facility].solution_value()) > 1e-6):
        print(f"\n Build a warehouse at location {facility + 1}.")


# In[ ]:


# Shipments from facilities to customers.
for customer, facility in assign.keys():
    if (abs(assign[customer, facility].solution_value()) > 1e-6):
        print(f"\n Supermarket {customer + 1} receives {round(assign[customer, facility].solution_value(), 2)} of its demand {demands[customer]} from Warehouse {facility + 1} .")


# In[ ]:




