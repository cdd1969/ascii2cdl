def read_file(path, comments=None):
    '''
    function read a file line by line, excluding comment lines and then combines list of lines into
    a single string.

    input:
        path     [str] - full path to file to be read
        comments [str] - a string whith which comment lines start, default is None
    out:
        file_content_str [str]
    '''
    import re
    with open(path, 'r') as f:
        file_content = f.readlines()
        file_content = [line.decode('utf8') for line in file_content]
        f.close()
    if comments is not None:  # remove comment lines that start with "//"
        file_content = [line for line in file_content if not re.sub('\s*?'+comments, comments, line).startswith(comments)]
    
    file_content_str = ''.join(file_content)  # join list of strings into single string
    
    if comments is not None:  # delete inline comments
        file_content_str = re.sub(comments+'.*?\n', '\n', file_content_str)
    return file_content_str


def get_parts(file_str):
    '''
    this function reads CDL syntax file and seperates three parts (by keywords : "dimensions:", "variables:",
    "data:") Following requirements have to be fullfilled:
        - keywords should be in order "dimensions:", "variables:", "data:"

    input:
        file_str [str]  - an input file as a string
    out:
        [list] - list of strings with parts
        nparts [int] - number of parts found in file
        fname [str]  - user defined name of netcdf file
    '''
    import re
    pat  = re.compile('.*?netcdf(.*?){.*', re.DOTALL)
    fname = re.match(pat, file_str).group(1)
    fname = fname.strip()+'.nc'
    nparts = 0

    if re.search('dimensions:', file_str): nparts += 1
    if re.search('variables:', file_str): nparts += 1
    if re.search('data:', file_str): nparts += 1

    if nparts == 3:
        pat1  = re.compile('.*dimensions:(.*?)variables:.*', re.DOTALL)
        pat2  = re.compile('.*variables:(.*?)data:.*', re.DOTALL)
        pat3  = re.compile('.*data:(.*?)}.*', re.DOTALL)
        part_data = re.match(pat3, file_str).group(1)
        part_vars = re.match(pat2, file_str).group(1)
        part_dims = re.match(pat1, file_str).group(1)
        return [part_dims, part_vars, part_data] , nparts, fname
    elif nparts == 2:
        pat1  = re.compile('.*dimensions:(.*?)variables:.*', re.DOTALL)
        pat2  = re.compile('.*variables:(.*?)}.*', re.DOTALL)
        part_vars = re.match(pat2, file_str).group(1)
        part_dims = re.match(pat1, file_str).group(1)
        return [part_dims, part_vars] , nparts, fname
    elif nparts == 1:
        pat1  = re.compile('.*dimensions:(.*?)}.*', re.DOTALL)
        part_dims = re.match(pat1, file_str).group(1)
        return [part_dims] , nparts, fname



def process_dimensions(dims_str, log=False):
    '''
    function seraches within a given string for parameters (see regex), trys to convert values to
    integer (string are also possible as "unlimited" or "*") and returns a dictionary with params
    
    input:
        dims_str [str] - part of the file with CDl dimension description
    out:
        dimensions [dict] - params that have been found ( key = name of the dimension, value = its value)
    '''
    sname = "process_dimensions():"
    import re
    params = re.findall('[\.\+\-\@\w]+\s*=\s*[\.\+\-\@\w\*]+', dims_str)
    dimensions = {}
    for p in params:
        key, val = p.split('=', 1)
        key, val = key.strip(), val.strip()
        try:
            val = int(val)
            if val < 1:
                err_msg = 'Dimension "{0}" has invalid size "{1}". Size should be any integer >0, "unlimited" or \
                            "*"(indicating that dimesion size is yet unknown, see create_netcdf.py)'.format(key, val)
                raise ValueError(err_msg)
        except:  #if dimension = unlimited or *
            if val in ['unlimited', 'Unlimited', 'UNLIMITED']:
                val = None  # default value for unlimited dim , whith netcdf4 library in python
            elif val == '*':
                pass
            else:
                err_msg = 'Dimension "{0}" has invalid size "{1}". Size should be any integer >0, "unlimited" or \
                            "*"(indicating that dimesion size is yet unknown, see create_netcdf.py)'.format(key, val)
                raise ValueError(err_msg)

        dimensions[key] = val

        if log: print sname, "dimension found >>> <{0}> of size <{1}>".format(key, val)
    return dimensions


def process_variables(vars_str, log=False):
    '''
    function seraches within a given string for variables (see regex) and returns a dictionary with their list
    
    input:
        vars_str [str] - part of the file with CDL variable description
    out:
        variables [dict] - variables that have been found, (key - name of the variable, value = [datatype, [dim1,dim2,...]])
                            Note: all values are stored as strings
    '''
    sname = "process_variables():"
    import re
    variables = {}
    # this is list with datatypes both supported by netcdf3(first row) and netcdf4(second row)
    dtype_list = ["char", "byte", "short", "int", "long", "float", "real", "double",
                    "ubyte", "ushort", "uint", "int64", "uint64", "string"]
    for dtype in dtype_list:
        vars_of_type = re.findall('\s*?'+dtype+'\s*(.*);', vars_str)
        #print dtype, '\t-->  ', vars_of_type
        vars = []
        for l in vars_of_type:
            var = re.findall('[\.\+\-\@\w]+?\s*\(\s*[\.\+\-\@\w\*,\s]+?\)', l)
            #print '\t'*5, l, '\t-->  ', var
            for v in var: vars.append(v)
            # now we have a list of strings like ["lat(lat)", "t(time,lat,lon", ...]
        #print vars
        
        # now for each variable extract dimensions and name
        for var in vars:
            if log: print var
            varname = re.match('([\.\+\-\@\w\s]+?)\(.*', var).group(1).strip()
            vardims = re.match('.*?\((.*?)\).*', var).group(1)
            vardims = vardims.split(',')
            for i, item in enumerate(vardims):  # ensure that there are no whitespaces
                vardims[i] = item.strip()
            variables[varname] = [dtype, vardims]

            if log: print sname, "variable found >>> <{0}> of type <{1}> and dimension <{2}>".format(varname, dtype, vardims)

    return variables


def check_variables_and_dimensions(dims, vars):
    '''
    functions iterates over variable dimensions and compares it to ones, that were
    defined in "dimensions:" part. Raises ValueError if an invalid dimension was
    specified

    input:
        dims [dict] - dimensions, created by function "process_dimensions()"
        vars [dict] - variables,  created by function "process_variables()"
    '''
    d = dims.keys()
    for key, val in vars.iteritems():       # val is a list [dtype, [dims]]
        for vd in val[1]:                   # val[1] is a list with dimensions
            if vd not in d:
                err_msg = 'Variable "{0}" has invalid dimension "{1}"'.format(key, vd)
                raise ValueError(err_msg)


def process_variables_attributes(vars_str, vars, log=False):
    '''
    function searches within a given text for attributes to variables which are defined within dictionary "vars"
    appends a dictionary "var_attributes" with attributes to the "vars"


    input:
        vars_str [str] - part of the file with CDL variables description
        vars [dict] - variables that have been found, (key - name of the variable, value = [datatype, [dim1,dim2,...]])
                            Note: all values are stored as strings. Created by function "process_variables()"
    '''
    sname = "process_variables_attributes():"
    import re

    for vn in vars.keys():
        var_attributes = {}   # dictionary to store found attributes
        raw_attrs = re.findall('.*'+vn+':(.*?);', vars_str)
        #print vn, '\t\t', '--->', '\t', raw_attrs
        for raw_a in raw_attrs:
            key, val = raw_a.split('=', 1)
            key = key.strip()  # removing whitespaces
            #print key
            val = re.sub('[\"\']', '', val)  # remove brackets indicating string format
            val = val.strip()  # removing whitespaces
            vals = val.split(',')   # list of values of a single attribute (i.e range = 0., 100.)
            for i, v in enumerate(vals):    # now convert items to desired type
                #print v
                if re.match('\s*\d+\.\d*\s*', v):  # if there is a . => float
                    vals[i] = float(v.strip())
                else:
                    try:
                        vals[i] = int(v.strip())    # else try => int
                    except ValueError:
                        vals[i] = v.strip()         # or leave as string
            if log: print sname, "variable '{0}', atribute found >>> {1} = {2}".format(vn, key, vals)
            var_attributes[key] = vals
            #print var_attributes
        vars[vn].append(var_attributes)


def process_global_attributes(vars_str, log=False):
    '''
    function searches within a given text for global attributes

    input:
        vars_str [str] - part of the file with CDL variable description

    out:
        glb_attributes [dict] - dictionary with global attributes (key = attr name, val = value)
    '''
    sname = "process_global_attributes():"
    import re
    glb_attributes = {}
    raw_attrs = re.findall('\s+?:(.*?);', vars_str)
    for raw_a in raw_attrs:
            key, val = raw_a.split('=', 1)
            key = key.strip()  # removing whitespaces
            if log: print sname, 'found global attribute --->  ', key
            val = re.sub('[\"\']', '', val)  # remove brackets indicating string format
            val = val.strip()  # removing whitespaces
            vals = val.split(',')   # list of values of a single attribute (i.e range = 0., 100.)
            for i, v in enumerate(vals):    # now convert items to desired type
                #print v
                if re.match('\s*\d+\.\d*\s*', v):  # if there is a . => float
                    vals[i] = float(v.strip())
                else:
                    try:
                        vals[i] = int(v.strip())    # else try => int
                    except ValueError:
                        vals[i] = v.strip()         # or leave as string
            glb_attributes[key] = vals
    
    if glb_attributes:
        return glb_attributes
    else:
        return None


def check_undefined_dimensions(dim_dict, metafname=None, log=False):
    '''
    function checks if there are any undefined dimensions ,if so - goes to metafile, and loads
    undefined dimensions first from data file

    input:
        dim_dict [dictionary] - dictionary, where keys - dimension names, values - dimension sizes.
                                Note: values could be any integer >0, None, or '*'
        metafname [str] - fullpath to metafile. Default = None
    out:
        dim_dict [dictionary] - modified input dictionary, where keys - dimension names, values - dimension sizes,
                                from now on without any undefined dimensions
                                Note: values could be any integer >0, None
        dims_vals [dict] - dictionary with information about unique values (sorted in ascending order) of a given dimensions
                            {"dim_name": [array of unique values], ...}
    '''
    import read_metafile
    import os

    
    path2metafile = os.path.split(metafname)[0]
    unknown_dims = []
    unknown_flg = False

    for name, val in dim_dict.iteritems():
        if val == '*':  # dim=* mean that dimension is unknown. first read it from data file
            unknown_dims.append(name)
            unknown_flg = True

    dims_vals = {}
    if unknown_flg:  # if there are unknown dimensions.... first read them from data file
        if metafname is not None:
            metadata = read_metafile.read_metadata(metafname)
            dims, dims_vals = read_metafile.getDimVal(metadata, path2metafile, unknown_dims, log=log)
            for d in dims.keys():
                if d not in unknown_dims:
                    err_msg = 'Dimension "{0}" declared in Metafile do not match any of the undefined dimension in CDL\
                                file {1}'.format(d, unknown_dims)
                    raise ValueError(err_msg)
                else:
                    dim_dict[d] = dims [d]
        else:
            err_msg = 'Metafile path is missing. CDL file declares variables with unknown dimension size: metafile is needed'
            raise ValueError(err_msg)
    #print dim_dict
    return dim_dict, dims_vals


def extend_dimensions_with_sizes(Vars, dims):
    '''
    function modifies "vars" dictionary, appending one list of integers to its value. List values are
    corresponding to the size of dimension located at same position in previous list


    input:
        dims [dictionary] - input dictionary, where keys - dimension names, values - dimension sizes,
                                from now on without any undefined dimensions
                                Note: values could be any integer >0, None
        vars [dictionary] - variables that have been found, (key - name of the variable, value = [datatype, [dim1,dim2,...], {atrributes}])
                            Note: all values are stored as strings. Created by function "process_variables()"

    out:
        vars [dictionary] - modified dictionary: variables that have been found, (key - name of the variable,
                            value = [datatype, [dim1_name,dim2_name,...], {atrributes}, [dim1_size,dim2_size,...]])
                            Note: value[0]  and value [1] are stored as strings. value[2] is list of integers.
                            Created by function "process_variables()"
    '''
    for vName, vVal in Vars.iteritems():
        dimVals = []
        for dimName in vVal[1]:
            if dimName in dims.keys():
                dimVals.append(dims[dimName])
            else:
                err_msg = 'dimension "{0}" not found in dictionary "dims"'.format(dimName)
                raise IndexError(err_msg)
        Vars[vName].append(dimVals)

    return Vars
