def replace_undefined_dimensions(file2modify, newFileName, dims, log=False):
    '''
    function reads CDL file, cycles through section dimensions: and replaces any undefined dims
    marked with star symbol "*". Note that this function does not overwrites your old CDL file.

    input:
        file2modify     - string containing file name of CDL to be modified
        newFileName     - string containing file name to be created
        dims            - dictionary containing information about dimensions. Is created with function
                          <read_cdl.process_dimensions()>, and is being processed by function <read_cdl.check_undefined_dimensions()>
                          keys - dimension names, values - dimension sizes
    '''
    sname = "replace_undefined_dimensions():"
    import re
    import os

    tempFilename = file2modify+'.tmp'



    inData = False
    with open(file2modify, 'r') as fi:
        with open(tempFilename, 'w+') as fo:
            for i, line in enumerate (fi):
                line = line.decode('utf8')
                if "data" in line:  # we stop if we encount keyword "data"
                    try:
                        line_without_comment = line.split('//').strip()
                    except: line_without_comment = line
                    if "data" in line_without_comment:
                        inData = True

                if len(line.split('//')) > 1:
                    lineNoComm = line.split('//')[0]  #split lines by comments
                    comm = '//'+line.split('//')[1]  #split lines by comments
                else:
                    lineNoComm = line
                    comm = ''

                m = re.findall('.*?=\s*?\*\s*?[\,\;].*?', lineNoComm)
                if m and not inData:
                    name = m[0].split('=')[0].strip()  # extract pure dimension name
                    # we have esured that dimension name is already in our list with previous functions
                    val = dims[name]
                    lineNew = re.sub('\*', str(val), lineNoComm)+comm
                    fo.write(lineNew)
                    if log: print sname, 'line <{0}>. Undefined dimensions <{1}> value has been changed from <*> to <{2}>'.format(i, name, val)
                else:
                    fo.write(line)

            fo.close()
        fi.close()
    
    try: os.remove(newFileName)  # if file exist - remove it rename() doesn't overwrite on Windows
    except: pass  # if file do not exist, do nothing
    os.rename(tempFilename, newFileName)
    if log: print sname, "renaming temp file into >>> {0}".format(newFileName)




def create_useCols_from_meta(metaData, Vars, varName, log=False):
    """
    function creates 'useColumn' list for a user-defined variable with name <varName>
    Aim is future correct reading with np.loadtxt

    input:
        metaData [dict] - dictionary with information from metaFile. Created with
                          read_metafile.read_metadata()
        Vars [dictionary] - dictionary: variables (key - name of the variable,
                            value = [datatype, [dim1_name,dim2_name,...], [dim1_size,dim2_size,...]])
                            Note: value[0]  and value [1] are stored as strings. value[2] is list of integers.
                            Created by function "read_cdl.extend_dimensions_with_sizes()"
        varName - a string containing name of the investigating variable (should match name in CDL file)

    out:
        useCols - a list with integers, indicating which columns to read from OBS file for a given variable
    """
    import re
    from operator import itemgetter

    sname = 'create_useCols_from_meta():'
    
    if None in Vars[varName][3]:
        err_msg = '"None" dimension encounted. It is a pointer for an unlimited dimension. Unlimited dimension is treated as dimension of size 1'
        if log: print err_msg
        Vars[varName][3][Vars[varName][3].index(None)] = 1  # making unlimited dimension as of size 1
        #err_msg = '"None" dimension encounted. It is a pointer for an unlimited dimension. Unlimited dimension arrays are a not supported'
        #raise ValueError(err_msg+'\n\n')
    

    useCols = []
    dimNames = Vars[varName][1]
    implicit_dims = []
    if log: print sname, "passed variable '{0}': {1}".format(varName, Vars[varName])
    for dimName in dimNames:
        for i, name in enumerate(metaData['columnDataNames']):
            if ((name == dimName) and (i not in useCols)):
                index = i
                useCols.append(index)
                if log: print sname, "dimension '{0}' >>> column index '{1}'".format(name, index)
                break

    if varName not in dimNames:  # if variable name is not same as dimension dame example: coordX(coordX)
        if log: print sname, "passed ColumnDataNames from metaFile", metaData['columnDataNames']
        for i, name in enumerate(metaData['columnDataNames']):
            if ((name == varName) and (i not in useCols)):  # if name in metaFile matches one in CDL (i.e. z and z >>> match, but z and z(0;0;1) >>> not match)
                if log: print sname, "values for '{0}' >>> column index '{1}'".format(name, i)
                useCols.append(i)
                break  # only one column for each varName is possible...
            elif ((re.sub('\(.*\)', '', name) == varName) and (i not in useCols)):  # if name in metaFile without brackets matches one in CDL (i.e.but z and z(0;0;1) >>> match)
                index = i
                # if in data file we have two columns in this order :    z(x;1), z(x;0)
                # we want to sort it into ascending order >>> z(x;0), z(x;1)
                lst = [name, [e for e in metaData['columnDataVarDims'][index] if isinstance(e, int)], index]
                # [name - as in metaFile, e - integer indicating index in dimension which is represented bz columns, index - index of column in OBS file]
                
                implicit_dims.append(lst)  #metaData['columnDataVarDims'][index] - is a list of dimensions from metaData (should contain one integer and rest are strings)
                if log: print sname, "values for '{0}' >>> column index '{1}'".format(name, index)


        # ------------------------------------------------------------------
        # ------------------ this section only for -------------------------
        # ------------------- implicit dims z(i,j,1) -----------------------
        # ------------------------------------------------------------------

        if len(implicit_dims) > 0:  # if we have encounted those kind of arrays... z(i,j,1) , z(i,j,2) , z(i,j,3) ...
            # now sort array <implicit_dims> acording to integer value in <implicit_dims[:][1]>
            implicit_dims.sort(key=itemgetter(1))  # sort list by second column....
            # append all those nasty columns in ascending order
            for i in implicit_dims[:]:
                columnIndex = i[2]
                useCols.append(columnIndex)

            # now check if number of columns is corresponding to dimension size...
            lst = []
            for i, name in enumerate(Vars[varName][1]):  # hardcopy of list Vars[varName][1] = [gridX, gridY, gridZ]
                if Vars[varName][3][i] != 1:            # excluding one-size dimensions
                    lst.append(name)
            #lst = [i for i in Vars[varName][1] if i Vars[varName][2]]
            for dn in metaData['columnDataVarDims'][index]:  # [gridX, gridY, 0] for example
                if dn in lst:
                    lst.remove(dn)
            if len(lst) == 1:
                pointer = Vars[varName][1].index(lst[0])
                implicitDimName = Vars[varName][1][pointer]  # 1 - dim names as strings, 3- dim sizes
                implicitDimSize = Vars[varName][3][pointer]

                if implicitDimSize != len(implicit_dims):
                    err_msg = 'Dimension <{0}> specified in CDL has size of <{1}>. Only <{2}> corresponding column names were found in metaFile ({3})\n'\
                                'Provide information for missing <{4}> columns in metaFile "columnDataNames"'.format(implicitDimName, implicitDimSize,
                                len(implicit_dims), [i[0] for i in implicit_dims], implicitDimSize - len(implicit_dims))
                    raise ValueError(err_msg+'\n\n')
            else:
                err_msg = 'Dimensions <{0}> of variable <{1}> not understood.\n Make sure only one integer index is present, and dimensions match CDL '\
                            '<{2}>'.format(metaData['columnDataVarDims'][index], varName, Vars[varName][1])
                raise ValueError(err_msg+'\n\n')

                

    if log: print sname, "useCols = {0}".format(useCols)
    return useCols




def make_cdl(cdlFname, metafname=None, outpath='', log=False):
    '''
    create a copy of existing CDL format file, where missing data is substituted with "*" sign
    and modify it file step by step:
    _________________________________

    1) reading CDL format file, extracting info from sections:
        "dimensions:",
        "variables:",
        !NOT IMPLEMENTED !    "data"

    2) reading observation data if nessesary (dimensions are unknown dim="*" )
    

    '''
    sname = 'make_cdl():'
    import shutil
    import read_cdl
    import os
    import read_metafile
    import funcs
    import re

    # first make a copy to work with
    path , fname = os.path.split(os.path.abspath(cdlFname))
    pathmeta , fnamemeta = os.path.split(os.path.abspath(metafname))
    name, extension = fname.split('.')
    #newFilename  = outpath+name+'_modified.'+extension
    tempFilename = cdlFname+'.tmp'
    newFileName = os.path.join(outpath, "_"+fname)
    #shutil.copyfile(cdlFname, cdlFname+'.bak')

    # proceed
    f = read_cdl.read_file(cdlFname, comments='//')
    parts, nparts, fname = read_cdl.get_parts(f)
    dims = read_cdl.process_dimensions(parts[0], log=log)
    Vars = read_cdl.process_variables(parts[1], log=log)
    read_cdl.process_variables_attributes(parts[1], Vars, log=log)
    read_cdl.check_variables_and_dimensions(dims, Vars)
    dimensions, udimension_arrays = read_cdl.check_undefined_dimensions(dims, metafname=metafname, log=log)
    Vars = read_cdl.extend_dimensions_with_sizes(Vars, dimensions)
    replace_undefined_dimensions(cdlFname, newFileName, dimensions, log=log)
    #replace_undefined_dimensions(cdlFname, newFilename, dims)
    metaData = read_metafile.read_metadata(metafname, log=log)
    # undefined_vars = read_cdl.get_undefVars()


    with open(newFileName, 'r') as fIn:
        if log: print sname, "creating temp file {0}".format(tempFilename)
        with open(tempFilename, 'w+') as fOut:
            for i, lineRaw in enumerate(fIn):  #cycling through lines in old file...
                lineRaw = lineRaw.decode('utf8')

                if len(lineRaw.split('//')) > 1:  # ignore comments
                    line = lineRaw.split("//")[0]
                else:
                    line = lineRaw

                if re.match('.*?=\s*\*.*', line):  # if * is present after sign = (undefined variable is here, cause there are already no undefined dimensions at this step)
                    uVarName = re.match('\s*?(.*?)\s*=.*', line).group(1).strip()
                    if log: print sname, "line {0} >>> Undefined variable '{1}'' found in CDL ".format(i+1, uVarName)
                    if uVarName in Vars.keys():
                        fOut.write('\t{0} =\n'.format(uVarName))  # first write variable name...

                        # creating array with data...
                        if log: print sname, 'Creating array based on: "{0}" = {1}'.format(uVarName, Vars[uVarName])
                        useCols = create_useCols_from_meta(metaData, Vars, uVarName, log=log)

                        if log: print sname, 'variable {0} >>> useCols = {1}'.format (uVarName, useCols)
                        obs = funcs.loadASCII(os.path.join(pathmeta, metaData['dataFname']), dtype=Vars[uVarName][0], delimiter=metaData['delimiter'],
                                              skiprows=metaData['skiprows'], usecols=useCols, log=log)
                        #for k ,v in Vars.iteritems(): print k, '>>>', v
                        if "_FillValue" in Vars[uVarName][2].keys():
                            fv = Vars[uVarName][2]["_FillValue"][0]
                        else:
                            fv = -999

                        data = funcs.create_array_from_data(Vars[uVarName][3], Vars[uVarName][1], uVarName, obs, fill_value=fv, log=log)

                        
                        # now write it to cdl in column order....
                        data = data.flatten(order="C")  # flatten array in column order as in C-language
                        if log: print sname, 'writing to files data-section values of variable <{0}>... be patient - this may take few minutes'.format(uVarName)
                        
                        for i, val in enumerate(data):  # write to file... string by string
                            if i != (data.size - 1):  # if not last element
                                fOut.write('\t\t{0} ,\n'.format(val))
                            else:  #if last element
                                fOut.write('\t\t{0} ;\n'.format(val))


                    else:
                        err_msg = 'CDL file contains undefined variable {0}, which is missing in dictionary "Vars"'.format(uVarName)
                        raise ValueError(err_msg+'\n\n')
                else:
                    if log : print sname, 'line {0} >>> no changes'.format(i+1)
                    fOut.write(lineRaw)  # if line without * => rewrite it
            fOut.close()
        fIn.close()

    try: os.remove(newFileName)  # if file exist - remove itrename() doesn't overwrite on Windows
    except: pass  # if file do not exist, do nothing
    os.rename(tempFilename, newFileName)
    if log: print sname, "renaming temp file into >>> {0}".format(newFileName)
