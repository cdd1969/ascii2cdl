from __future__ import division
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pylab import squeeze
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mpl_toolkits.basemap import Basemap
# --------------------------------------------------
#                   User Input
# --------------------------------------------------
OUTPATH = '//Widar/home/ak2stud/Nick/python_scripts/ascii2netcdf/work_in_progress/general/'


OUTFILE = 'test_unlim.nc'
a = Dataset(str(OUTPATH+OUTFILE), mode='r')

# ----------------------------
# -------- bathymetry --------
# ----------------------------
vars = a.variables

z = squeeze(vars['z'][:, :])
z = np.fliplr(z)  # flip horizontally
x = squeeze(vars['GridX'][:])
y = squeeze(vars['GridY'][:])

f = plt.figure()
f.suptitle('Bathymetry', fontsize=20)
ax = plt.gca()
im = ax.imshow(z.T, extent=(x.min(), x.max(), y.min(), y.max()),
           interpolation='nearest', cmap=cm.gist_rainbow)
# create an axes on the right side of ax. The width of cax will be 5%
# of ax and the padding between cax and ax will be fixed at 0.05 inch.
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="2%", pad=0.05)
plt.colorbar(im, cax=cax)
plt.show()

a.close()


"""
OUTFILE = 'test_GSD.nc'
#OUTFILE = 'grain_size_GermanNorthSea2012.nc'
a = Dataset(str(OUTPATH+OUTFILE), mode='r')
vars = a.variables
print vars
s = np.arange(12)
for sed_class in s:
    
    gsd1 = squeeze(vars['gsd'][:, :, [sed_class]])
    gsd1 = np.fliplr(gsd1)  # flip horizontally
    x = squeeze(vars['GridX'][:])
    y = squeeze(vars['GridY'][:])

    f = plt.figure(figsize=(8, 8))
    f.suptitle('Grain size distribution (class {0}: {1})'.format(sed_class, sed_class), fontsize=20)
    ax = plt.gca()
    im = ax.imshow(gsd1.T, extent=(x.min(), x.max(), y.min(), y.max()),
               interpolation='none', cmap=cm.gist_rainbow)
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label(label=u'%', fontsize=20)
    figname = '_gsd_{0}_gb2012'.format(sed_class)
    f.savefig(OUTPATH+figname+'.pdf', bbox_inches='tight')
a.close()

"""
print 'done'