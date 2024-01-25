import math
import numpy
import numpy as np
def formula():
    corr_fact = 1
    a = 1
    n = 1
    m = 1
    e = math.e
    print(e)
    #RANGE OF A,N,M     a(32, 159) n(0.525, 0.93) m(2.243, 1.004)
    #Typical a,n,m a = 20 n = 0.8 m = 0.75
    suction = [0.01, 0.66, 4, 11, 16, 66, 148, 250, 400, 650, 800, 1260, 1410, 2070, 2950, 4680, 7630, 12260]
    volum_water_content = [0.210, 0.207, 0.140, 0.031, 0.008, 0.005, 0.003, 0.003, 0.002, 0.002, 0.002, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
    #TODO: matric suction find
    print(math.log(5, e))
    for suc in suction:
        ans = volum_water_content[0]/((math.log(e+(suc/a)**n, e))**m)
        print(ans)

