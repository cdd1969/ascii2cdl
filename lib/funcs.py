from __future__ import division
import numpy as np
import time


def create_array_from_data(dim_list, dim_nlist, varName, OBS, fill_value=-999, log=False):
    """
    Function creates an array <a> of given dimensions <dim_list>, stores values of variable
    <varName> located in <OBS> array

    input:
        dim_list                - list of integers of arrays dimension sizes
                                  (i.e. dim_list=[2, 3, 2] will create 3d-array with 2 elements along first and
                                   third dimension, and 3 elements along second dimension )
        dim_nlist               - list of strings corresponding to dimension names in list "dim_list"
        varName                 - string indicating current variable name
        
        fill_value              - any integer or float representing array filling value
        OBS                     - 2D input numpy array, dimensions (..., 3)
                                any number of lines; 3 columns
    out:
        a                       - numpy array of shape "dim_list", filled with values from array "OBS"
    """
    sname = 'create_array_from_data():'
    import numpy as np
    import time
    t1 = time.time()

    cellsdone = 0
    if log: print sname, 'Creatin array with dimensions: {0}'.format(dim_list)


    # ------------------------------------------------------------------------------------------------
    # in OBS array, last column is representing data, while every column before - data-array dimension
    # as example, 3-column OBS array with x,y,z information is treated as 2D array with 1st dimenion of x
    # and 2nd dimension of y, z values are stored within matrix(x,y)
    # Note, that dimensions of size 1 are ignored (because there is no need to create complex filling routine)

    # compare number of columns in OBS with array dimension
    ne_dim = 0   # number of effective (non-one size) dimensions
    if log: print sname, "Calculating number of dimensions (nd) of a variable. Currently nd=0"
    for d in dim_list:
        if log: print sname, "\tdim_size = '{0}'".format(d)
        if d != 1:
            ne_dim += 1
            if log: print sname, "\tnd += 1. nd = {0}".format(ne_dim)

    if ne_dim == 1:    # if we have variables-dimensions rulers z(z)
        obs_ncols = 1  # actually we can have as well 1D arrays but two column OBS z(x)
        p = 0          # therefore hard-code "obs_ncols" and "p"
    elif ne_dim == 2:
        obs_ncols = len(OBS[0, :])
        p = 1
    elif ne_dim == 3:  # hardcoded
        obs_ncols = 4
        p = 1
    else:
        p = np.NaN
        err_msg = '{0} is a non-supported number of dimensions in array'.format(ne_dim)
        raise ValueError(err_msg+'\n\n')

    if ne_dim != (obs_ncols - p):
        err_msg = 'Number of columns in OBS array ({0}) passed to function "create_array_from_data()" does not'\
                ' match number of non-one size dimensions (len({1})+1 = {2}).\n\n in OBS array, last column is representing'\
                ' data, while every column before - data-array dimension.\nAs example, 3-column OBS array with'\
                ' x,y,z information is treated as 2D array with 1st dimenion of x \nand 2nd dimension of y. Where z'\
                ' values are stored within matrix(x,y). Note that dimensions of size 1 are ignored\n'.format(obs_ncols, dim_list, ne_dim+1)
        raise ValueError(err_msg+'\n\n')



    # ------------------------------------------------------------------------------------------------
    # finally fill array
    #if log: print sname, 'Writing values to netcdf...'
    


    # ------------------------------------------------------------------------------------------------
    # ------------------------------------ fill 1D array ---------------------------------------------
    # ------------------------------------------------------------------------------------------------
    if ne_dim == 1:   # if we have variable-dimension
        if varName in dim_nlist:  # if it is a dimension-variable example: coordX(coordX)
            a = np.unique(OBS)
            cellsdone = a.size
        else:  # if it is not a dimension-variable
            OBS = sortArrayXY(OBS, print_s=2)
            a = OBS[:, 1]  # take second column of data
        if log: print sname, 'working with 1d array.... >>> shape= ', a.shape


    # ------------------------------------------------------------------------------------------------
    # ------------------------------------fill 2D array-----------------------------------------------
    # ------------------------------------------------------------------------------------------------
    elif ne_dim == 2:  # if we are filling 2D array....a.shape=(dim1,dim2) (may have more than 2 dimension, but others are of size 1)
        dim1_array = np.unique(OBS[:, 0])
        dim2_array = np.unique(OBS[:, 1])


        a = np.zeros([len(dim1_array), len(dim2_array)])
        a[:] = fill_value
        if log: print sname, 'working with 2d array.... >>> shape= ', a.shape

        # ------------------------------------------------------------------------------------------------
        # sort OBS array in ascending oder first by 1st column, and then by 2nd
        OBS = sortArrayXY(OBS, print_s=2, log=log)

        dim1i, dim2i = 0, 0  # indexes
        dim1_v0, dim2_v0 = OBS[0, 0], OBS[0, 1]  # values

        nDataPoints = len(OBS)
        for dim1_v, dim2_v, val, line in zip(OBS[:, 0], OBS[:, 1], OBS[:, 2], xrange(nDataPoints)):
            if np.fmod(line, 50000) == 0 and log:   # this IF is for timing prints
                t = time.time()
                timeElapsed = t-t1
                percentsDone = line/nDataPoints*100
                try:
                    timeLeft = timeElapsed*(100./percentsDone-1)/60.
                except:
                    timeLeft = np.NaN
                print '\t\t[{2:3.1f} %]\t{0} cells filled in {1:.0f} seconds  --->  Time remaining {3:3.1f} minutes'.format(line, timeElapsed, percentsDone, timeLeft)
            #print "Reading line %i, \t" % (line+1), dim1_v, dim2_v, val
            
            #find out indexes for filling value. Only valid because sorting has been done (sortArrayXY)
            if dim1_v > dim1_v0:
                dim1i += 1
            dim2i = np.where(dim2_array  == dim2_v) [0][0]

            # fill variable ( one single value), here variable_toFill[lati, loni] is a value
            a[dim1i, dim2i] = val
            cellsdone += 1
            dim1_v0 = dim1_v


    # ------------------------------------------------------------------------------------------------
    # ------------------------------------fill 3D array-----------------------------------------------
    # ------------------------------------------------------------------------------------------------
    #
    #       filling 3D array <a> of shape=(dim1,dim2, dim3). <OBS> array is column based , 1st column - dim1[:]; 2nd - dim2[:],
    #       3rd - a[:,:,0], 4th - a[:,:,1], 5th - a[:,:,2], etc...
    #
    #       if we are filling 3D array....a.shape=(dim1,dim2, dim3) (may have more than 3 dimension, but others are of size 1)
    elif ne_dim == 3:
        dim1_array = np.unique(OBS[:, 0])  # number of unique items in x direction
        dim2_array = np.unique(OBS[:, 1])  # number of unique items in y direction
        dim3_size  = len(OBS[0]) - 2          # number of columns in OBS - 2

        if log: print [len(dim1_array), len(dim2_array), dim3_size]
        a = np.zeros([len(dim1_array), len(dim2_array), dim3_size])
        a[:] = fill_value
        if log: print sname, 'working with 3d array.... >>> shape= ', a.shape

        # ------------------------------------------------------------------------------------------------
        # sort OBS array in ascending oder first by 1st column, and then by 2nd
        OBS = sortArrayXY(OBS, print_s=2, log=log)

        dim1i, dim2i = 0, 0  # indexes
        dim1_v0, dim2_v0 = OBS[0, 0], OBS[0, 1]  # values

        nDataPoints = len(OBS)
        for dim1_v, dim2_v, vals, line in zip(OBS[:, 0], OBS[:, 1], OBS[:, 2::], xrange(nDataPoints)):
            
            if np.fmod(line, 50000) == 0 and log:   # this IF is for timing prints
                t = time.time()
                timeElapsed = t-t1
                percentsDone = line/nDataPoints*100
                try:
                    timeLeft = timeElapsed*(100./percentsDone-1)/60.
                except:
                    timeLeft = np.NaN
                print '\t\t[{2:3.1f} %]\t{0} cells filled in {1:.0f} seconds  --->  Time remaining {3:3.1f} minutes'.format(line, timeElapsed, percentsDone, timeLeft)
            

            #find out indexes for filling value. Only valid because sorting has been done (sortArrayXY)
            if dim1_v > dim1_v0:
                dim1i += 1
            dim2i = np.where(dim2_array == dim2_v) [0][0]

            # fill variable ( one single value), here variable_toFill[lati, loni] is a value
            a[dim1i, dim2i] = vals
            cellsdone += 1
            dim1_v0 = dim1_v
    else:
        err_msg = '{0} is a non-supported number of dimension in array'.format(ne_dim)
        raise ValueError(err_msg+'\n\n')
    
    # ------------------------------------------------------------------------------------------------
    # --------------------------swap axes (x,y, 12) >>> (12,x,y)--------------------------------------
    # -----------------------------       If nessesary    --------------------------------------------
    dim_list_without_ones = tuple([d for d in dim_list if d!=1])  # dim_list excluding one-size dimensions
    if a.shape != dim_list_without_ones :  #if shapes are not equal(excluding 1-size dims). (a - array we work with, dim_list - user-defined shape)
        if len(a.shape) == len(dim_list_without_ones):
            if log: print sname, 'Attempting to swap axes in array ( {0} >>> {1} )'.format(a.shape, dim_list_without_ones)
            for index, d in enumerate(dim_list_without_ones):
                if a.shape[index] != d:
                    a = np.swapaxes(a, index, a.shape.index(d))
            if a.shape == dim_list_without_ones:
                if log: print sname, 'Axis swapped ( {0} == {1} ) successfully'.format(a.shape, dim_list_without_ones)
                pass
        else:
            err_msg = "internal array has shape {0}. Cannot swap axes to receive array {1}. Number of dimensions is not equal".fromat (a.shape, dim_list_without_ones)
            raise ValueError(err_msg)
    # ------------------------------------------------------------------------------------------------
    # --------------------------------reshape array into requested dimensions-------------------------
    # ------------------------------------------------------------------------------------------------
    if log: print sname, 'Reshape array ( {0} >>> {1} )'.format(a.shape, dim_list)
    a = a.reshape(dim_list)
    if log: print sname, 'Data has been stored within array of shape <{0}>. Note that <{2}> out of <{3}> cells were filled with data, rest - with fill_value=<{1}>'\
                         .format(a.shape, fill_value, cellsdone, a.size)
    return a


def fillNetCDF_Variable(variable_toFill, OBS, longitudes, nlat, nlon, obs_spm_valMin, obs_spm_valMax):
    """
    Function fills input 2D-grid(nlat*nlon) "variable_toFill" with scattered data stored in OBS array,
    clipping values within range [obs_spm_valMin:obs_spm_valMax]

    input:
        variable_toFill         - Numpy array - grid to be filled with dimensions (nlat,nlon).
        OBS                     - 2D input numpy array, dimensions (..., 3)
                                any number of lines; 3 columns
        longitudes              - 1D numpy array with all unique longitude values stored
                                  in asceding order(length=nlon)
        nlat, nlon              - number of unique lat, lon coordinates [integer]
        obs_spm_valMin/Max      - clipping values [float]

    """
    cellsdone = 0

    print 'fillNetCDF_Variable(): Writing values to netcdf...'
    t3 = time.time()
    lati, loni = 0, 0
    latOld, lonOld = OBS[0, 0], OBS[0, 1]

    nDataPoints = len(OBS)
    for lat, lon, spm, line in zip(OBS[:, 0], OBS[:, 1], OBS[:, 2], xrange(nDataPoints)):
        # this IF is for timing prints
        if np.fmod(line, 50000) == 0:
            t = time.time()
            timeElapsed = t-t3
            percentsDone = line/nDataPoints*100
            try:
                timeLeft = timeElapsed*(100./percentsDone-1)/60.
            except:
                timeLeft = np.NaN
            print '\t[{2:3.1f} %]\t{0} cells filled in {1:.0f} seconds  --->  Time remaining {3:3.1f} minutes'.format(line, timeElapsed, percentsDone, timeLeft)
        #print "Reading line %i, \t" % (line+1), lat, lon, spm
        
        #find out indexes for filling value. Only valid because sorting has been done (sortArrayXY)
        if lat > latOld:
            lati += 1
        loni = np.where(longitudes  == lon) [0][0]

        # write value to netcdf
        if spm < obs_spm_valMin:
            spm = obs_spm_valMin
            print 'obs_line {0}: observation value {1} is not within valid range [{2}:{3}] \t => \t saving {2}'.format(line+1, spm, obs_spm_valMin, obs_spm_valMax)
        if spm > obs_spm_valMax:
            spm = obs_spm_valMax
            print 'obs_line {0}: observation value {1} is not within valid range [{2}:{3}] \t => \t saving {2}'.format(line+1, spm, obs_spm_valMin, obs_spm_valMax)
        
        # fill variable ( one single value), here variable_toFill[lati, loni] is a value
        variable_toFill[lati, loni] = spm
        cellsdone += 1
        latOld = lat

    print 'fillNetCDF_Variable(): Warning! {1} cells filled out of {0}'.format(nlat*nlon, cellsdone)


def twoD_fillNetCDF_Variable(variable_toFill, OBS, longitudes, nlat, nlon):
    """
    Function fills input 2D-grid(nlat*nlon) "variable_toFill" with scattered data stored in OBS array

    input:
        variable_toFill         - Numpy array - grid to be filled with dimensions (nlat,nlon).
        OBS                     - 2D input numpy array, dimensions (..., ....)
                                any number of lines; any number of columns
        longitudes              - 1D numpy array with all unique longitude values stored
                                  in asceding order(length=nlon)
        nlat, nlon              - number of unique lat, lon coordinates [integer]
        obs_spm_valMin/Max      - clipping values [float]

    """
    cellsdone = 0
    
    print 'twoD_fillNetCDF_Variable(): Writing values to netcdf...'
    t3 = time.time()
    lati, loni = 0, 0
    latOld, lonOld = OBS[0, 0], OBS[0, 1]

    nDataPoints = len(OBS)
    for lat, lon, spm, line in zip(OBS[:, 0], OBS[:, 1], OBS[:, 2::], xrange(nDataPoints)):
        if np.fmod(line, 50000) == 0:
            t = time.time()
            timeElapsed = t-t3
            percentsDone = line/nDataPoints*100
            try:
                timeLeft = timeElapsed*(100./percentsDone-1)/60.
            except:
                timeLeft = np.NaN
            print '\t[{2:3.1f} %]\t{0} cells filled in {1:.0f} seconds  --->  Time remaining {3:3.1f} minutes'.format(line, timeElapsed, percentsDone, timeLeft)
        
        if lat > latOld:
            lati += 1
        loni = np.where(longitudes  == lon) [0][0]
        # fill variable (all columns in one step!), here variable_toFill[lati, loni] is an array
        variable_toFill[lati, loni] = spm[:]

        cellsdone += 1

        latOld = lat
    print 'twoD_fillNetCDF_Variable(): Warning! {1} cells filled out of {0}'.format(nlat*nlon, cellsdone)


def arrayReplace_WGS84withUTM(array, lati, loni, precision=2):
    """
    Replaces values of Lat, Lon in a given 2D numpy-array with projected coordinates
    performing WGS-84 ---> UTM conversion , where lati, loni indexes of columns
    with latitudes and longitudes (in example below lati=0, loni=1).
    Latitude column is replaced with easting/westing(x-coordinate), and Longitude
    is replaced with northing/southing (y-coordinate)
    Values are rounded by user-defined presision rate (number of decimals),
    default precision=2 means that values are rounded up to cm

    Library "utm" is required
    Download via : https://pypi.python.org/pypi/utm

    Array example(without header):
        lat         lon        val
    ----------------------------------
      3.30970    52.11391     4.1846
      3.31372    52.11391     3.9219
      3.31774    52.11391     4.1661
      3.32176    52.11391     4.0596
      3.32579    52.11391     4.3199
      3.32981    52.11391     4.0187

    """
    import time
    import utm
    import numpy

    print 'arrayReplace_WGS84withUTM(): starting coordinates convertion'
    tStart = time.time()
    #if precision == ''
    numberOfLines = len(array)
    x, y, zoneNumber, zoneLetter = utm.from_latlon(array[0, lati], array[0, loni])
    zones = ['{0}{1}'.format(zoneNumber, zoneLetter)]
    print "\tSelected Zone: {0}{1}".format(zoneNumber, zoneLetter)
    for lat, lon, line in zip(array[:, lati], array[:, loni], xrange(numberOfLines)):
        if line < 10: print array[line, :]
        x, y, zoneNumber, zoneLetter = utm.from_latlon(lat, lon)
        zone = '{0}{1}'.format(zoneNumber, zoneLetter)
        zones.append(zone)

        array[line, lati] = x
        array[line, loni] = y
        if line < 10: print array[line, :]
    tEnd = time.time()
    print 'arrayReplace_WGS84withUTM(): data located in zones: {0}'.format(numpy.unique(zones))
    print 'arrayReplace_WGS84withUTM(): coordinates have been converted in {0:.0f} seconds'.format(tEnd-tStart)


def monotonical (array1D):
    '''
    function checks if given 1Darray is monotonously increasing.
    It cycles through array and checks the difference between its value.

    Input:
        arra1D      - sorted in asceding order numpy array
    '''
    i = 1
    error = None
    step = array1D[1] - array1D[0]
    while i < len(array1D):
        #print array1D[i]
        stepi = array1D[i] - array1D[i-1]
        if not stepi == step:
            print 'ERROR: stepi={2} is not equal to dold={3}, between [{0},{1}]'.format(i, i-1, stepi, step)
            error = True
        i += 1
    if not error:
        print "array is monotonously increasing with step: %d" % step
    else:
        print "array is not monotonously increasing"


def loadASCII(fname, dtype='float', comments='#', delimiter=None, converters=None, skiprows=0, usecols=None, log=False):
    '''
    requires numpy, time

    function loads column based ascii file into numpy array, and writes required time. For details
    refer to numpy.loadtxt
    
    Input:
        fname       - datafile full path+name [string]
        dtype       - output data type [string]
        comments    - The character used to indicate the start of a comment
        delimiter   - The string used to separate values. By default, this is any whitespace.
        converters  - A dictionary mapping column number to a function that will convert that column to a float.
                      E.g., if column 0 is a date string: converters = {0: datestr2num}. Converters can also
                      be used to provide a default value for missing data (but see also genfromtxt):
                      converters = {3: lambda s: float(s.strip() or 0)}.
        skiprows    - Skip the first skiprows lines; default: 0.
        usecols     - Which columns to read, with 0 being the first. For example, usecols = (1,4,5) will extract
                      the 2nd, 5th and 6th columns. The default, None, results in all columns being read.
    Output:
        OBS         - numpy array
    '''
    import time
    import numpy as np
    sname = 'loadASCII():'

    if log: print sname, 'Reading file: {0}... be patient - this may take few minutes'.format(fname)
    t1 = time.time()
    OBS  = np.loadtxt(fname, dtype=dtype, comments=comments, delimiter=delimiter, converters=converters,
                 skiprows=skiprows, usecols=usecols)
    t2 = time.time()
    if log: print sname, 'Observation file has been read succesfully in {0:.0f} seconds'.format(t2-t1)
    return OBS


def sortArrayXY(a, log=False, print_s=0):
    import time
    '''
    Function sorts 2Darray (number of columns should be >=2) by two actions:
        1) sort by first column
        2) sort by second column not changing 1st column
    For example on a small array with comments refer to function "sortArrayXY_EXAMPLE()".
    You can simply execute this file alone (see "__main__:" for details)
    
    Example:
        [[ 1.   1.   0.1]             [[ 1.   1.   0.1]
         [ 2.   1.   0.2]              [ 1.   2.   0.5]
         [ 3.   1.   0.3]              [ 1.   3.   0.9]
         [ 4.   1.   0.4]              [ 2.   1.   0.2]
         [ 1.   3.   0.9]              [ 2.   2.   0.6]
         [ 2.   3.   1. ]     --->     [ 2.   3.   1. ]
         [ 3.   3.   1.1]              [ 3.   1.   0.3]
         [ 4.   3.   1.2]              [ 3.   2.   0.7]
         [ 1.   2.   0.5]              [ 3.   3.   1.1]
         [ 2.   2.   0.6]              [ 4.   1.   0.4]
         [ 3.   2.   0.7]              [ 4.   2.   0.8]
         [ 4.   2.   0.8]]             [ 4.   3.   1.2]]
    
    Input:
        a   -   1D or 2D numpy array
        print_s - integer indicating how many whitespaces to print before text in console
                   just for a nice output
    '''
    t1 = time.time()
    nx = len(a)  # length in axis=0

    # sort by 1st column
    a = a[a[:, 0].argsort()]
    # sort part of the array a[j:1,0] , second column part
    j = 0
    i = 1
    while i < nx:
        if a[i, 0] != a[i-1, 0]:
            b = a[j:i, :]
            a[j:i, :] = b[b[:, 1].argsort()]
            j = i

        # taking care of last section
        if i == nx-1:
            b = a[j:, :]
            a[j:, :] = b[b[:, 1].argsort()]
        i += 1
    t2 = time.time()
    if log: print '{1}sortArrayXY(): Array has been sorted in {0:.3f} seconds'.format(t2-t1, ' '*print_s)
    return a


def sortArrayXY_EXAMPLE(a):
    '''
    THIS IS AN EXAMPLE OF FUNCTION sortArrayXY()
    a file "input_sort_file_example.txt" should be created in the same directory as this script.
    This file should contain following strings (without indents):

    1 1 0.1
    2 1 0.2
    3 1 0.3
    4 1 0.4
    1 3 0.9
    2 3 1.0
    3 3 1.1
    4 3 1.2
    1 2 0.5
    2 2 0.6
    3 2 0.7
    4 2 0.8
    '''

    nx = len(a)  # length in axis=0
    print a
    print ('-'*20)
    a = a[a[:, 0].argsort()]
    print a
    # sort part of the array a[j:1,0]
    j = 0
    i = 1
    while i < nx:
        print i, a[i, 0]
        try:
            if a[i, 0] != a[i-1, 0]:
                print '{0} != {1} => slicing a[{2}:{3}]'.format(a[i, 0], a[i-1, 0], j, i)
                b = a[j:i, :]
                print '\tReplace:'
                print a[j:i, :]
                print '\tWith:'
                print b[b[:, 1].argsort()]
                a[j:i, :] = b[b[:, 1].argsort()]
                j = i
                print '\tResult:'
                print a
        except:
            pass
        if i == nx-1:
            b = a[j:, :]
            print '\tReplace:'
            print a[j:i, :]
            print '\tWith:'
            print b[b[:, 1].argsort()]
            a[j:, :] = b[b[:, 1].argsort()]
            print '\tResult:'
            print a
        i += 1
    print ('-'*20)
    print a
    return a


if __name__ == "__main__":
    import h5py as hdf
    PATH = '//Widar/home/ak2stud/Nick/python_scripts/ascii2netcdf/'
    OBS  = np.loadtxt(PATH+'input_sort_file_example.txt', delimiter=' ', skiprows=0)
    #sortArrayXY_EXAMPLE(OBS)
    #print hdf
    #1.092 - (75.20-8.733)/2./(10**6)/24./365. - x - 1.346 = -0.05
    x  = 1.092 - (75.24-8.733)/2./(10**6)*24.*365. - 1.346 +0.05
    print -x*2.*10**6
