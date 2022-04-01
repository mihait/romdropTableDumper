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
                '%d':    "d"}.get(tformat, '.3f')

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

    def _mr_proper(self, value, type_format, expression):
        tfmt = self._translate_format(type_format)
        x = value
        if tfmt == '08x':
            return "{}".format(hex(x))
        elif tfmt == 'd':
            return "{:{tfmt}}".format(int(eval(expression)), tfmt = tfmt)
        else:
            return "{:{tfmt}}".format(float(eval(expression)), tfmt = tfmt)

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
            result.append(self._mr_proper(buff[0], tprops['format'], tprops['toexpr']))
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

    def list_category_and_name(self):
        for i in self.defs_json['roms']['rom']['table']:
            if self.verbose:
                print("./romdumper.py dump-table -c '{}' -n '{}'  ###table type: {}".format(i['@category'], i['@name'], i['@type']))
            else:
                print("./romdumper.py dump-table -c '{}' -n '{}'".format(i['@category'], i['@name']))


    def _order_table(self, table_data, x, y, swapxy):
        tr_data=[]
        if swapxy == 'true':
            for i in range(len(y)):
                line=[]
                k = i
                for j in range(len(x)):
                    line.append(table_data[k])
                    k+=len(y)
                tr_data.append(line)
        else:
            for i in range(len(y)):
                line=[]
                for j in range(len(x)):
                    line.append(table_data[i+j])
                tr_data.append(line)
        return tr_data

    def _dump_1d(self, data, name):
        print("\nTable dump\n%s\n----" % name)
        for i in data:
            print(i)

    def _dump_2d(self, table_data, axis_data, axis_name, name):
        print("\nTable dump\n%s\n----" % name)
        if axis_name == 'X Axis':
            for i in axis_data:
                print("{0:>6}".format(i), end = '')
            print("")
            for i in table_data:
                print("{0:>6}".format(i), end = '')
            print("")
        else:
            for i in range(len(axis_data)):
                print(" {:>8} {:>5}".format(axis_data[i],table_data[i]))

    def _dump_3d(self, table_data, x_data, y_data, swapxy, name):
        print("\nTable dump\n%s\n----" % name)
        
        tr_data = self._order_table(table_data, x_data, y_data, swapxy)
    
        rjst = 9
        #print table
        print("-x-".rjust(rjst), end='')

        # x axis top
        for i in x_data:
            print("{}".format(i).rjust(rjst), end = '')
        print("\n")

        z = 0
        for j in y_data:
            print("{} ".format(y_data[z]).rjust(rjst), end ='')
            a = tr_data[z]
            for l in a:
                print("{}".format(l).rjust(rjst), end='')
            print("\n")
            z+=1
        return

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
            self._dump_1d(tdata, name)
            return

        #2D table
        if desired_table['@type'] == "2D":
            axis_name = desired_table['table']['@type']
            axis_data = self._get_table_data(data_addr = desired_table['table']['@address'], data_len = desired_table['table']['@elements'], scaling = desired_table['table']['@scaling'])
            self._dump_2d(tdata, axis_data, axis_name, name)
            return

        #3D table
        if desired_table['@type'] == "3D":
            for t in desired_table['table']:
                if t['@type'] == 'X Axis':
                    x_data = self._get_table_data(data_addr = t['@address'], data_len = t['@elements'], scaling = t['@scaling'])
                if t['@type'] == 'Y Axis':
                    y_data = self._get_table_data(data_addr = t['@address'], data_len = t['@elements'], scaling = t['@scaling'])
            swapxy = desired_table['@swapxy'] 
            self._dump_3d(tdata, x_data, y_data, swapxy, name)


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

