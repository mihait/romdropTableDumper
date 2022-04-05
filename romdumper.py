#!/usr/bin/env python3

#modules imports
import os
import sys
import argparse

# invoke me from anywhere
current_path = os.path.dirname(sys.argv[0])
if len(current_path) > 0:
    sys.path.insert(0, current_path)

#import dumper et all
from src import *

#romdrop metadata file
def_file = 'path/to/romdrop/metadata/l831eg.xml'
#patched rom file
rom_file = '/path/to/roms/L831EG_Rev_xyz.bin'
#rom_all_text dump file
dump_file = 'current_rom_dump.txt'

#csv delimiter
csv_delimiter = ';'

#verbose level
verbose = False

def rd_hdl():
    return dumper.RomDumper(rom_file=rom_file, xml_def_file=def_file, verbose = verbose, csv_delimiter = csv_delimiter)

def list_all(args):
    rd_hdl().list_category_and_name()

def dump_table(args):
    rd_hdl().dump_table(args.category, args.name)

def dump_all(args):
    rd_hdl().dump_all(dump_file)

def dump_all_cli(args):
    rd = dumper.RomDumper(rom_file=args.rom_file, xml_def_file=args.def_file, verbose = verbose, csv_delimiter = csv_delimiter)
    rd.dump_all(args.output_file)

def main():

    global csv_delimiter

    parser = argparse.ArgumentParser(description='romdrop table(s) dumper')
    parser.set_defaults(func=lambda x: parser.print_help())
    subparsers = parser.add_subparsers(help='sub-command help')
    #list all
    parser_list_all = subparsers.add_parser('list-all', help='list all tables')
    parser_list_all.set_defaults(func=list_all)
    #dump table
    parser_dump_table = subparsers.add_parser('dump-table', help='dump one table by category and name')
    parser_dump_table.add_argument('-c', action='store', dest = 'category', required = True,
        help='category containing table, see list-all')
    parser_dump_table.add_argument('-n', action='store', dest = 'name', required = True,
        help='table name in category, see list-all')
    parser_dump_table.add_argument('--csv', action='store_const', const = 'csv', required = False,
        help='dump table with field separator for csv import')
    parser_dump_table.set_defaults(func=dump_table)
    #dump all tables - use script defined rom/def/out files
    parser_dump_all = subparsers.add_parser('dump-all', help='dump all tables using the rom/def/output files defined inside the script')
    parser_dump_all.add_argument('--csv', action='store_const', const = 'csv', required = False,
        help='dump table with field separator for csv import')
    parser_dump_all.set_defaults(func=dump_all)
    #dump all tables - use command line arguments for rom/def/output files
    parser_dump_all_cli = subparsers.add_parser('cli-dump-all', help='dump all tables to file using command line specified parameters for rom/def/outfile')
    parser_dump_all_cli.add_argument('-r', action='store', dest = 'rom_file', required = True,
        help='binary rom file')
    parser_dump_all_cli.add_argument('-d', action='store', dest = 'def_file', required = True,
        help='xml metadata for the rom binary')
    parser_dump_all_cli.add_argument('-o', action='store', dest = 'output_file', required = True,
        help='desired output file')
    parser_dump_all_cli.add_argument('--csv', action='store_const', const = 'csv', required = False,
        help='dump table with field separator for csv import')
    parser_dump_all_cli.set_defaults(func=dump_all_cli)

    #ensure we have all opts specified
    try:
        options = parser.parse_args()
    except:
        sys.exit(1)

    #add csv delim if requested
    if vars(options).get('csv'):
        if options.csv is False:
            csv_delimiter = ''
    else:
        csv_delimiter = ''

    #do requested action
    options.func(options)
    sys.exit(0)


if __name__ == "__main__":
    main()
