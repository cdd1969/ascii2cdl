from __future__ import division
import os
import sys


def create_netcdf_dimensions(ncdf_grp, dim_dict):
    '''
    function uses netcdf4 Dataset object (or group), and creates a dimensions from passed dictionary
    wheneever a dimension was specified as *, function skips it, adding to unknown-dimension list, and
    activating an unknown-dimension flag. If an unknown dimension is present, user should first read
    it from data.

    input:
        ncdf_grp ['Dataset' or 'Group' object of 'netCDF4' class] - object where to create dimensions
        dim_dict [dictionary] - dictionary, where keys - dimension names, values - dimension sizes.
                                Note: values could be any integer >0, None, or '*'
    '''
    unknown_dims = []
    unknown_flg = False
    for name, val in dim_dict.iteritems():
        if val != '*':
            ncdf_grp.createDimension(name, size=val)
        else:   # dim=* mean that dimension is unknown. first read it from data file
            unknown_dims.append(name)
            unknown_flg = True
    #return unknown_flg, unknown_dims



def fill_undefined_dimension_variables(ncdf_grp, dims_vals):
    """
    function fills variables (of a given netcdf group or dataset) having same name as dimensions that have
    been specified as undefined in CDL syntax (with =*)

    input:
        ncdf_grp - instance of netcdf Dataset or Group
        dims_vals [dict] - dictionary with information about unique values (sorted in ascending order) of a given dimensions
                        {"dim_name": [array of unique values], ...}
    """
    print '-'*50+'\nPrinting netcdf vars: ', ncdf_grp.variables
    for var_name, value_array in dims_vals.iteritems():
        if var_name in ncdf_grp.variables:
            ncdf_grp.variables[var_name] = value_array
        else:
            err_msg = 'Variable "{0}" declared in Metafile do not match any of the variables in NETCDF file {1}'.format(var_name, ncdf_grp.variables)
            raise ValueError(err_msg)


def create_netcdf_variable(ncdf_grp, variables, zlib=False, complevel=4, shuffle=True, fletcher32=False,
                            contiguous=False):
    '''
    function handles a netcdf dataset (or group) and creates variables with certain parameters that are
    imported with dictionary "variables".

    input:
        ncdf_grp - instance of netcdf Dataset or Group
        variables [dict] - dictionary with strored variable info. This dictionary has a format as below...
                            {"var_name": ["dtype", [dimension1, dimension2,...], {"attribute1_name": attribute1_val, "attribute2_name": attribute2_val, ...}], ...}
        other - inherited from method "createVariable()"
    '''
    #convert datatype from cdl syntax into netcdf syntax
    dtype_cdl_to_netcdf = {"char":   'c',
                           "byte":   'b',
                           "short":  's',
                           "int":    'i4',
                           "long":   'l',
                           "float":  'f4',
                           #"real":  '???',  #not implemented yet
                           "double": 'f8',
                           "ubyte":  'u1',
                           "ushort": 'u2',
                           "uint":   'u4',
                           "int64":  'i8',
                           "uint64": 'u8',
                           #"string": '????'  #not implemented yet
                           }
    # iterate over dictionary with variables, dimensions, attributes
    for varname, params in variables.iteritems():
        #print 'creating variables: varname: {0} \t\t params: {1}'.format(varname, params)
        dtypeCDL, dims, attrs = params[0], params[1], params[2]
        
        dims = tuple(dims)  # converting list to tuple (is nessesary for .createVariable() method)
        
        # check dtype....
        if dtypeCDL in dtype_cdl_to_netcdf.keys():
            dtype = dtype_cdl_to_netcdf[dtypeCDL]
        else:
            err_msg = 'Variable "{0}"" has an unsupported datatype "{1}". Valid dtype:"char","byte",\
                        "short,"int","long","float","double,"ubyte","ushort,"uint":,"int64","uint64"'\
                        .format(varname, dtypeCDL)
            raise ValueError(err_msg)

        #search for _FillValue in attributes, and set it as a parameter for method createVariable()
        if len(attrs) == 0: fill_value = None
        for attr_name, attr_val in attrs.iteritems():
            if attr_name == '_FillValue':
                fill_value = attr_val[0]
            else:
                fill_value = None

        # create a variable instance
        #print 'creating variables: varname {0} \t\t fill_value: {1}'.format(varname, fill_value)
        ncdf_var = ncdf_grp.createVariable(varname, dtype, fill_value=fill_value, dimensions=dims, zlib=zlib, complevel=complevel,
                    shuffle=shuffle, fletcher32=fletcher32, contiguous=contiguous)

        #now set attributes...
        for attr_name, attr_val in attrs.iteritems():
            if not attr_name == '_FillValue':   #_FillValue attribute must be set when variable is created (using fill_value keyword to createVariable)
                if attr_val:  #if list "attr_val" is not empty.
                    setattr(ncdf_var, attr_name, tuple(attr_val))


def append_netcdf_glb_attrs(ncdf_grp, attributes):
    '''
    function appends global attributes to instance "ncdf_grp"

    input:
        ncdf_grp - instance of netcdf Dataset or Group
        attributes [dict] - dictionary with attributes. Has following format
                            {"attribute1_name": attribute1_val, "attribute2_name": attribute2_val, ...}
    '''
    import time
    ncdf_grp.history = 'Created ' + time.ctime(time.time())
    if attributes is not None:
        for attr_name, attr_val in attributes.iteritems():
            #print '\t', attr_name
            setattr(ncdf_grp, attr_name, tuple(attr_val))


def create_ncdf(fname, dimensions, variables, metafname=None, global_attributes=None, path='', mode='w', clobber=False,
                format='NETCDF4_CLASSIC'):
    '''
    function creates an netCDF file (appends attributes, dimensions, variables)

    NO DATA IS STORED within created variables

    input:
        fname [str] - filename of netcdf file to be created
        path [str] - path of resulting netcdf file. Default is ''
        dimensions [dict]  - dictionary with information about dimensions, where keys - dimension names,
                                values - dimension sizes.
                                Note: values could be any integer >0, None, or '*'
        variables [dict] -  dictionary with strored variable info. This dictionary has a format as below...
                            {"var_name": ["dtype", [dimension1, dimension2,...], {"attribute1_name": attribute1_val, "attribute2_name": attribute2_val, ...}], ...}
        global_attributes [dict] - dictionary with global attributes. Default is "None"
        other - inherited from netCDF4.Dataset()
    '''
    from netCDF4 import Dataset
    import read_cdl

    #initialize
    root_grp = Dataset(path+fname, mode=mode, clobber=clobber, format=format)
    # make global attributes
    append_netcdf_glb_attrs(root_grp, global_attributes)
    #create dimensions
    dimensions, udimension_arrays = read_cdl.check_undefined_dimensions(dimensions, metafname=metafname)
    create_netcdf_dimensions(root_grp, dimensions)
    # create variables
    create_netcdf_variable(root_grp, variables)
    # fill variables of undefined dimensions
    fill_undefined_dimension_variables(root_grp, udimension_arrays)

    # set DATA

    #Closing ncdf
    root_grp.close()
    print 'File created succesfully: %s' % (path+fname)


def make_netcdf(cdlFname, metafname=None, outpath=''):
    '''
    creates netcdf file step by step:
    _________________________________

    1) reading CDL format file, extracting info from sections:
        "dimensions:",
        "variables:",
        !NOT IMPLEMENTED !    "data"

    2) reading observation data if nessesary (dimensions are unknown dim="*" )
    
    3) creates netcdf file

    !NOT IMPLEMENTED ! 4) read metadata file supplied with data, extracts information about how to process data

    !NOT IMPLEMENTED ! 5) read data and fill it into netcdf
    '''
    import read_cdl

    f = read_cdl.read_file(cdlFname, comments='//')
    parts, nparts, fname = read_cdl.get_parts(f)
    dims = read_cdl.process_dimensions(parts[0])
    glb_attrs = read_cdl.process_global_attributes(parts[1])
    vars = read_cdl.process_variables(parts[1])
    read_cdl.check_variables_and_dimensions(dims, vars)
    read_cdl.process_variables_attributes(parts[1], vars)
    create_ncdf(fname, dims, vars, metafname=metafname, global_attributes=glb_attrs, path=outpath, clobber=True)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------

if __name__ == '__main__':
    Path = os.path.dirname(sys.argv[0])
    cdlFname = Path+"/cdl_test1.cdl"
    meta = Path+"/metadata_1.txt"
    make_netcdf(cdlFname, metafname=meta , outpath='//KEPHEUS/studenten/ak2stud/Nick/python_out/')
