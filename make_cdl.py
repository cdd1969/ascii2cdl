#!/usr/bin/python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import os
    import sys
    import inspect
    import getopt

    # use this if you want to include modules from a subfolder
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "lib")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    
    from modify_cdl import make_cdl

    def read_arguments(argv):
        inputfile = ''
        metafile = ''
        log = False
        run = 0
        err_msg = '\t -h <help>\n\t -i <input CDL filename>\n\t -m <input meta file> \n\t-l(optional flag for console log)\n\t Example: $ python make_cdl.py -i myfile.cdl -m mymetafile.txt -l'
                
        try:
            opts, args = getopt.getopt(argv, "?hli:m:", longopts=['help', 'ifile=', 'mfile='])
            if len(args) > 0 or len(opts) > 3:
                print 'invalid input'
                print err_msg
                sys.exit()

        except getopt.GetoptError:
            print 'Unable to read arguments'
            print err_msg
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-h', '--help', '-?'):
                print err_msg
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfile = arg
                run += 1
            elif opt in ("-m", "--mfile"):
                metafile = arg
                run += 1
            elif opt in ('-l'):
                log = True
            else:
                print 'Invalid argument: {0} {1}'.format(opt, arg)
                print err_msg
                sys.exit()
        if run == 2:
            return inputfile, metafile, log
        else:
            print 'Not enough arguments'
            print err_msg
            sys.exit()



    log = False
    Path_script, _ = os.path.split(os.path.abspath(sys.argv[0]))
    cdlFname, meta, log = read_arguments(sys.argv[1:])
    Path_cdl, cdlFname = os.path.split(os.path.abspath(cdlFname))
    Path_meta, meta = os.path.split(os.path.abspath(meta))


    make_cdl(os.path.join(Path_cdl, cdlFname), metafname=os.path.join(Path_meta, meta), log=log, outpath=Path_script)
    print 'File created successfully >>> ', os.path.join(Path_script, '_'+cdlFname)
