from handle_ncdf import make_netcdf
import os
import sys

if __name__ == '__main__':
    Path = os.path.dirname(sys.argv[0])
    cdlFname = Path+"/cdl_test1.cdl"
    meta = Path+"/metadata_1.txt"
    make_netcdf(cdlFname, metafname=meta , outpath='//KEPHEUS/studenten/ak2stud/Nick/python_out/')
