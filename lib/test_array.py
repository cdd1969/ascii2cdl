import numpy as np
import funcs

dims = [2, 3, 4]
a = np.arange(2*3*4)
a = a.reshape(dims)

"""
print a.shape
print a.ndim
print a
b = a.flatten(order="C")
print b
iterator = 0
for i in xrange(2):
    for j in xrange(3):
        for k in xrange(4):
            print "// array ({0}, {1}, {2})".format(i, j, k)
            print b[iterator]
            iterator += 1
"""
"""
obs = funcs.loadASCII('BathymetryGermanNorthSea2012.csv', delimiter=";", skiprows=1)
x = np.unique(obs[:, 0]).size
y = np.unique(obs[:, 1]).size
dimL = [x, y, 5]
obs = funcs.create_array_from_data(dimL, obs, fill_value=-999.)
"""

a = np.arange(24).reshape(3, 4, 2)
b1 = np.array([True, True, False, 100])             # first dim selection
print a
print '-'*25


name = "a"
dimName = "a"
i = 5
useCols = [1,2,3,4]
if name == dimName and i not in useCols:  # if name in metaFile matches one in CDL (i.e. z and z >>> match, but z and z(0;0;1) >>> not match)
    print 'HEEEY'