def getDimVal(meta, path2metafile,  unknownDims, log=False):
    '''
    function calculates the size of dimensions marked in metafile. To do that, it reads a columnDataNames
    of corresponding data and takes number of unique values

    input:
        meta [dict] - dictionary with information from metadata file
        path2metafile - string containing path to directory where metafile is located
        unknownDims  - list of strings, containing names of unknown dimensions
    out:
        dims [dict] - dictionary with information about dimension size
                        {"dim_name": dimension_size, ...}
        dims_vals [dict] - dictionary with information about unique values (sorted in ascending order) of a given dimensions
                        {"dim_name": [array of unique values], ...}
    '''
    import os
    import numpy as np
    
    sname = 'getDimVal():'
    if log:
        print sname, "Passed as input:"
        print sname, "metafile info...:"
        for k, v in meta.iteritems():
            print sname, "\t{0} >>> {1}".format(k, v)
        print sname, "unknown dimensions: {0}".format(unknownDims)


    #which rows to skip
    fname = meta['dataFname']
    #fname = meta['dataFname']
    skp = meta['skiprows']
    dlm = meta['delimiter']

    #which columns to read
    dims = {}  # resulting dictionary val=[column_to_be_read]
    dims_vals = {}  # resulting dictionary val=[array of values with this dimension]
    for dim in unknownDims:  #cycle through every unknown dimension in a list
        dims[dim] = []
        # column should be taken from file
        for i, name in enumerate(meta['columnDataNames']):
            if dim == name:
                column = i
                dims[dim].append(column)
                break

    # now read data
    for dim_name, val in dims.iteritems():  # cycle again throug dimensions and read corresponding columns
        column = val[0]
        col = np.loadtxt(os.path.join(path2metafile, fname), delimiter=dlm, skiprows=skp, usecols=val)
        values = np.unique(col)
        dim_size = len(values)
        dims[dim_name] = dim_size  # rewrite value with a number of unique values in a column to dictionary
        dims_vals[dim_name] = values  # array with unique values in a column to dictionary sorted in ascending order

    return dims, dims_vals


def get_dataFromStr(string, dtype='str'):
    import re
    try:
        string = string.split('#')[0].strip()
    except:  # there is no #
        pass
    #print "working with string: ["+string+']'
    f = string.split('=')[1].strip()

    if dtype == "str":
        if f in ['None', 'none', 'NONE']:
            f = None
    
    elif dtype == "int":
        f = int(f)
    
    elif dtype == "list":
        if f in ['None', 'none', 'NONE']:
            f = None
        else:
            lst = f.split(',')
            f = [item.strip() for item in lst]          # remove trailing and leading whitespaces

    elif dtype == "list_ints":
        if f in ["all", "All", 'ALL']:
            f = None                                # we want to pass this argument to np.loadtxt() as usecols
        else:
            lst = f.split(',')
            f = [int(item) for item in lst]
    
    elif dtype == "column_names_list":
        lst = f.split(',')
        f = []
        lst = [item.strip() for item in lst]          # remove trailing and leading whitespaces
        for item in lst:
            f.append(re.sub("\s", "", item))        # remove all whotespaces
            #if "(" in item:                         # remove possible brackets ( spm(:;:;0) >>> spm )
            #    f.append(item.split('(')[0].strip())
            #else:
            #    f.append(item)

    elif dtype == "column_brackets_of_names_list":
        lst = f.split(',')
        lst = [item.strip() for item in lst]          # remove trailing and leading whitespaces
        f = []
        for item in lst:
            if '(' in item:
                sizes = [dim.strip() for dim in re.match('.*\((.*)\).*', item).group(1).split(';')]  # splits content in brackets by semicolon <;>
                for i, s in enumerate(sizes):
                    try: sizes[i] = int(s)  # try to convert to integer
                    except: sizes[i] = s
                f.append(sizes)
            else:
                f.append(None)         # remove possible brackets ( spm(:;:;0) >>> spm )

    return f


def read_metadata(fname, log=False):
    #try:
    sname = 'read_metadata():'


    with open(fname, 'r') as f:
        file_content = f.readlines()
        file_content = [line.decode('utf8') for line in file_content]
        f.close()
    #except:
    #    error_msg = 'file not found "{0}"'.format(fname)+str(sys.exc_info())
    #    raise ValueError(error_msg)
    #print file_content
    #file_content_str = ''.join(file_content)

    # remove comment lines that start with "#"
    file_content = [line.strip() for line in file_content if not line.strip().startswith('#')]
    a = {}
    for line in file_content:
        if   line.startswith(u'dataFname'):
            a['dataFname'] = get_dataFromStr(line, dtype='str')
        elif line.startswith(u'skiprows'):
            a['skiprows'] = get_dataFromStr(line, dtype='int')
        elif line.startswith(u'delimiter'):
            a['delimiter'] = get_dataFromStr(line, dtype='str')
        elif line.startswith(u'columnDataNames'):
            a['columnDataNames'] = get_dataFromStr(line, dtype='column_names_list')
            a['columnDataVarDims'] = get_dataFromStr(line, dtype='column_brackets_of_names_list')

    if log:
        print sname, "reading metafile..."
        for key, val in a.iteritems():
            print sname, "\t\t{0} >>> {1}".format(key, val)
        print sname, "-"*50
    return a

