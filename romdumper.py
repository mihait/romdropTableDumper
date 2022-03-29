#!/usr/bin/env python3

#modules imports
import os
import sys
import getopt

# invoke me from anywhere
current_path = os.path.dirname(sys.argv[0])
if len(current_path) > 0:
        sys.path.insert(0, current_path)

#import dumper et all
from src import *

#romdrop metadata file
def_file = '/path/to/romdrop/metadata/l831eg.xml'
#patched rom file
rom_file = '/path/to/roms/L831EG_Rev_xxxxx.bin'

#init
rd = dumper.RomDumper(rom_file=rom_file, xml_def_file=def_file)

#uncomment this line and comment the above for extra output
#rd = dumper.RomDumper(rom_file=rom_file, xml_def_file=def_file, verbose = True)

def show_help():
    print("WARNING - EXPERIMENTAL !\n")
    print("Usage:")
    print("./romdumper.py -c 'category' -t 'name'")
    print("./romdumper.py -l\n")
    print("Edit romdumper.py and set the paths to your rom and definition!")

def main(argv):
    category = ''
    name = ''
    listall = ''
    try:
        opts, args = getopt.getopt(argv,"hc:t:l",["category=","table-name=","list-all"])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_help()
        elif opt in ("-c", "--category"):
            category = arg
        elif opt in ("-n", "--table-name"):
            name = arg
        elif opt in ("-l", "--list-all"):
            listall = 'listall'

    if listall:
        rd.list_category_and_name()
        sys.exit(0)
    elif category and name:
        rd.dump_table(category=category, name=name)
        sys.exit(0)
    else:
        print("Too few arguments!")
        show_help()

if __name__ == "__main__":
   main(sys.argv[1:])


