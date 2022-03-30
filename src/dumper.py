import struct
import json
import xmltodict
import sys

class RomDumper():

    def __init__(self, rom_file, xml_def_file, verbose = False):
        self.rom_file = rom_file
        self.xml_def_file = xml_def_file
        self.verbose = verbose

        #load rom 
        with open(self.rom_file, 'rb') as r:
            self.rom_data = bytearray(r.read())
        #parse xml and convert to json
        with open(self.xml_def_file, 'r') as f:
            data_dict = xmltodict.parse(f.read())
        self.defs_json = json.loads(json.dumps(data_dict))

    def _translate_format(self, tformat):
        return {
                '%0.0f': ".0f",
                '%0.1f': ".1f",
                '%0.2f': ".2f",
                '%0.3f': ".3f",
                '%0.4f': ".4f",
                '%08x' : "08x",
                '%d':    ".3f"}.get(tformat, '.3f')

    def _type_len(self, tlen):
        return {
                'float': 4,
                'uint8': 1,
                'uint16': 2,
                'uint32': 4
                }.get(tlen)

    def _type_fmt(self, tfmt):
        return {
                'float': "f",
                'uint8': "B",
                'uint16': "H",
                'uint32': "I"
                }.get(tfmt)

    def _get_scaling_props(self, scaling):
        for i in self.defs_json['roms']['rom']['scaling']:
            if i['@name'] == scaling:
                return {
                        'toexpr': str(i['@toexpr']).replace('^','**'),
                        'frexpr': i['@frexpr'],
                        'format': i['@format'],
                        'storagetype': i['@storagetype'],
                        'endian': i['@endian']
                        }

    def _get_table_data(self, data_addr, data_len, scaling):

        tprops = self._get_scaling_props(scaling)
        if self.verbose:
            print(tprops)
        tlen = self._type_len(tprops['storagetype'])

        start  = int(data_addr, 16)
        tsize  = start +  (int(data_len) * tlen)
        tdata  = self.rom_data[start:tsize] 

        n = 0
        result = []
        tfmt = {'little': "<", 'big': ">"}.get(tprops['endian']) + self._type_fmt(tprops['storagetype'])
        
        for i in range(int(data_len)):
            buff = struct.unpack(tfmt, tdata[n:n+tlen])
            if tprops['format'] == '%08x':
                result.append(hex(buff[0]))
            elif tprops['format'] == '%d':
                x = int(buff[0])
                result.append(eval(tprops['toexpr']))
            else:
                x = float(buff[0])
                result.append(eval(tprops['toexpr']))
            n = n + tlen

        if len(result) == int(data_len):
            return result

    def _table_format(self, scaling_table):
        for i in self.defs_json['roms']['rom']['scaling']:
            if i['@name'] == scaling_table:
                data_format = i['@format'] 
        if self.verbose:
            print("scaling lookup format: %s " % data_format)
        return self._translate_format(data_format)

    def _table_tofr_expr(self, scaling_table):
        for i in self.defs_json['roms']['rom']['scaling']:
            if i['@name'] == scaling_table:
                toexpr = i['@toexpr']
                frexpr = i['@frexpr']
        if self.verbose:
            print("scaling to/fr expr: {} ---  {}".format(toexpr, frexpr))
        return (toexpr, frexpr)

    def list_category_and_name(self):
        for i in self.defs_json['roms']['rom']['table']:
            if self.verbose:
                print("./romdumper.py --category '{}' --table-name '{}'  ###table type: {}".format(i['@category'], i['@name'], i['@type']))
            else:
                print("./romdumper.py --category '{}' --table-name '{}'".format(i['@category'], i['@name']))


    def dump_table(self, category, name):
        for i in self.defs_json['roms']['rom']['table']:
            if i['@category'] == category and i['@name'] == name:
                desired_table = i

        if not 'desired_table' in locals():
            print("table not found! check input and def.")
            return

        #table data
        tdata = self._get_table_data(data_addr = desired_table['@address'], data_len = desired_table['@elements'], scaling = desired_table['@scaling'])

        if self.verbose:
            print("Found: {} <---> {}  LEN: {}".format(category, name,desired_table['@elements']))
            print(json.dumps(desired_table, indent=4, sort_keys=True))
            print("Data format: %s (from scaling table)" % self._table_format(desired_table['@scaling']))

        #1D table
        if desired_table['@type'] == "1D":
            tdfmt = self._table_format(desired_table['@scaling'])
            print("\nTable dump\n%s\n----" % name)
            for i in tdata:
                if tdfmt == '08x':
                    tdfmt = ''
                print("{:{fmt}}".format(i, fmt=tdfmt))
            return

        #2D table
        if desired_table['@type'] == "2D":
            print("\nTable dump\n%s\n----" % name)
            tdfmt = self._table_format(desired_table['@scaling'])

            if desired_table['table']['@type'] == 'X Axis':
                xdata = self._get_table_data(data_addr = desired_table['table']['@address'], data_len = desired_table['table']['@elements'], scaling = desired_table['table']['@scaling'])
                #xtfmt = self._table_format(desired_table['@scaling'])
                #ignore x, y axis formatting until we figure out why it's .0f in some cases
                xtfmt = '.3f'
                for i in xdata:
                    print("{0:>6{fmt}}".format(i,fmt=xtfmt), end = '')
                print("")
                for i in tdata:
                    print("{0:>6{fmt}}".format(i,fmt=tdfmt), end = '')
                print("")
                return
            if desired_table['table']['@type'] == 'Y Axis':
                ydata = self._get_table_data(data_addr = desired_table['table']['@address'], data_len = desired_table['table']['@elements'], scaling = desired_table['table']['@scaling'])
                #ytfmt = self._table_format(desired_table['@scaling'])
                #ignore x, y axis formatting until we figure out why it's .0f in some cases
                ytfmt = '.3f'
                for i in range(len(ydata)):
                    print(" {:>8{fmt}}".format(ydata[i], fmt=ytfmt), end = '')
                    print(" {:>5{fmt}}".format(tdata[i], fmt=ytfmt))
                return

        #3D table
        if desired_table['@type'] == "3D":
            print("\nTable dump\n%s\n----" % name)
            for t in desired_table['table']:
                if t['@type'] == 'X Axis':
                    xdata = self._get_table_data(data_addr = t['@address'], data_len = t['@elements'], scaling = t['@scaling'])
                    #xtfmt = self._table_format(desired_table['@scaling'])
                    #ignore x, y axis formatting until we figure out why it's .0f in some cases
                    xtfmt = '.3f'
                if t['@type'] == 'Y Axis':
                    ydata = self._get_table_data(data_addr = t['@address'], data_len = t['@elements'], scaling = t['@scaling'])
                    #ytfmt = self._table_format(desired_table['@scaling'])
                    #ignore x, y axis formatting until we figure out why it's .0f in some cases
                    ytfmt = '.3f'

            
            tdfmt = self._table_format(desired_table['@scaling'])

            tr_data=[]

            if desired_table['@swapxy'] == 'true':
                #
                #print(tdata)
                for i in range(len(ydata)):
                    line=[]
                    k = i
                    for j in range(len(xdata)):
                        line.append("{:{fmt}}".format(tdata[k], fmt = tdfmt))
                        k+=len(ydata)
                    tr_data.append(line)
            else:
                for i in range(len(ydata)):
                    line=[]
                    for j in range(len(xdata)):
                        line.append("{:{fmt}}".format(tdata[i+j], fmt = tdfmt))
                    tr_data.append(line)
                print(tr_data)

            rjst = 9
            #print table
            print("-x-".rjust(rjst), end='')

            # x axis top
            for i in xdata:
                print("{:{fmt}}".format(i, fmt=xtfmt).rjust(rjst), end = '')
            print("\n")
            
            z = 0
            for j in ydata:
                print("{:{fmt}} ".format(ydata[z], fmt=ytfmt).rjust(rjst), end ='')
                a = tr_data[z]
                for l in a:
                    print("{}".format(l).rjust(rjst), end='')
                print("\n")
                z+=1
            return


    def dump_all(self, filename):
        #dump all tables to file
        print("Dumping all tables to file...")
        original_stdout = sys.stdout
        with open(filename, 'w') as f:
            sys.stdout = f
            for i in self.defs_json['roms']['rom']['table']:
                self.dump_table(category = i['@category'], name = i['@name'])
                print("---END---")
            sys.stdout = original_stdout
        print("Done!")


