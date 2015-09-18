from pylab import squeeze
import netCDF4
import numpy as np
from matplotlib import pyplot as plt



if __name__ == "__main__":
    OUTPATH = '//KEPHEUS/studenten/ak2stud/Nick/python_out/general/'
    #OUTFILE = 'nick_netcdf.nc'
    OUTFILE = 'test.nc'
    
    a = netCDF4.Dataset(OUTPATH+OUTFILE, mode='r')
    print a
    vars = a.variables
    dims = a.dimensions
    print '*'*50
    print dims

    for var in vars:
        print '-'*50
        print var, vars[var]

# 425250,6003750,49.26,6.43,3.64,3.65,3.53,3.02,7.18,4.19,3.2,2.41,2.41,11.07
