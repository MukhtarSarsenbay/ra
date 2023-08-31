import math
import matplotlib.pyplot as plt
from scipy.optimize import minimize

#blocks for the parameters
tetta_s=[0.299,0.2985,0.2982,0.2976,0.2968,0.2966,0.2962,
0.2928,0.2902,0.289,0.2873,0.2847,0.2762,
0.263,0.2524,0.2433,0.2353,0.2044,0.1822,0.1649,0.1507,0.1389,0.1242,0.1055,0.0966,0.0803,0.04469125529313592,0.026313920990893178,0.011396562863493323,0.0011731620611407224,0.00041096933572304915,2.4140971529591052e-05,
]
a=1#as a test
n=1#as a test
m=1#as a test
soil_suction_r=10000#as a test
e=math.exp(1)
T_s=72.75*10**(-3)
soil_suction=[0.01,0.0979,0.1967,0.4,0.7,0.8,1,3,5,6,7.5,10,20,40,59.9964,80,100,200,300,400,500,600,750,1000,1150,1500,3000,5000,10000,50000,100000,500000,]
water_content = []
pore_radius = []
derivation = []


# Block of code for the 3rd formula - Water content
def formula3(value, value2, a, n, m, soil_suction_r):
    ln1 = math.log(1 + float(value) / float(soil_suction_r))
    ln2 = math.log(1 + (10 ** 6) / float(soil_suction_r))
    ln3 = math.log(e + (float(value / float(a))) ** float(n))
    overall_formula = float(value2) * (1 - float(ln1) / float(ln2)) * ((1 / float(ln3)) ** float(m))
    return overall_formula

# Block of code for the 4th formula - Derivation
def formula4(value, a, n, m, soil_suction_r, T_s):
    ln1 = math.log(1 + (float(value) / soil_suction_r))
    ln2 = math.log(1 + (10 ** 6) / soil_suction_r)
    ln3 = math.log(e + ((float(value / a)) ** n))
    block1 = float(1 - (ln1 / ln2))
    block2 = float(m * n * ((float(value / a) ** (n - 1))))
    block2_1 = float(a * (e + ((float(value / a)) ** n))) * (ln3 ** (m + 1))
    block2_2 = block2 / block2_1
    block3 = float(1 / (value + soil_suction_r))
    block4 = float(1 / (math.log(1 + (10 ** 6) / soil_suction_r)))
    block5 = float(1 / (ln3 ** m))
    second_formula_1 = block1 * block2_2
    third_formula = block3 * block4 * block5
    second_formula = second_formula_1 + third_formula
    return second_formula, float(2 * T_s) / float(value)

# Block of code to call the third formula and fourth formula functions
for value in range(len(soil_suction)):
    water_content.append(formula3(soil_suction[value], 0.299, a, n, m, soil_suction_r))
    derivation_value, pore_radius_value = formula4(soil_suction[value], a, n, m, soil_suction_r, T_s)
    derivation.append(derivation_value)
    pore_radius.append(pore_radius_value)

#Block of code to finish 4th formula
for value in range(len(soil_suction)):
    derivation[value]=derivation[value]*soil_suction[value]

# Define the objective function for optimization
def objective(variables):
    a, n, m, soil_suction_r = variables
    error_sum = 0
    for i in range(len(soil_suction)):
        predicted_water_content = formula3(soil_suction[i],0.299, a, n, m, soil_suction_r)
        error = (((tetta_s[i] - predicted_water_content) / tetta_s[i]) ** 2)
        error_sum += error
    print("error sum=",error_sum)
    return error_sum

# Set initial values for optimization,
x0 = [0.1, 0.1,0.1,0.1]

# Set bounds for the variables (optional)
bounds = [(0.1,None), (0.1, 6), (0.1, 6), (0.1,None)]


# Perform optimization
result = minimize(objective, x0,method='SLSQP',bounds=bounds)
optimal_a, optimal_n, optimal_m, optimal_soil_suction_r = result.x

#to draw a new graph
a=optimal_a
n=optimal_n
m=optimal_m
soil_suction_r=optimal_soil_suction_r
water_content.clear()
derivation.clear()
pore_radius.clear()

for value in range(len(soil_suction)):
    water_content.append(formula3(soil_suction[value], 0.299, a, n, m, soil_suction_r))
    derivation_value, pore_radius_value = formula4(soil_suction[value], a, n, m, soil_suction_r, T_s)
    derivation.append(derivation_value)
    pore_radius.append(pore_radius_value)

# Block of code to finish 4th formula
for value in range(len(soil_suction)):
    derivation[value] = derivation[value] * soil_suction[value]

# Print the optimal values
print("Optimal values:")
print("a =", optimal_a)
print("n =", optimal_n)
print("m=",optimal_m)
print("soil_suction_r =", optimal_soil_suction_r)



# Plot the graphs
#3rd graph
plt.plot(soil_suction, water_content)
plt.xlabel('Soil suction, \u03C8 (kPa) ')
plt.ylabel('Water content, w')
plt.title("Soil-water characteristics curve")
plt.plot(soil_suction,tetta_s,'x',markersize=10,color="blue")
plt.xscale('log')
plt.show()


#4th graph
plt.plot(pore_radius, derivation)
plt.xlabel('Pore Radius, r (mm)')
plt.ylabel('Derivation')
plt.title("Pore-size distribution")
plt.xscale('log')
plt.xlim(max(pore_radius), min(pore_radius))
plt.show()



