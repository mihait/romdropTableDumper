import struct
import json
import xmltodict
import array

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


    def _get_table(self, data_addr, data_len):
        start  = int(data_addr, 16)
        tsize  = start +  (int(data_len)*4)
        tdata  = self.rom_data[start:tsize]
        n = 0
        result = []
        for i in range(int(data_len)):
            result.append(struct.unpack('>f', tdata[n:n+4]))
            n = n + 4
        if len(result) == int(data_len):
            return result
        return 0

    def _translate_format(self, tformat):
        return {
                '%0.0f': ".0f",
                '%0.1f': ".1f",
                '%0.2f': ".2f",
                '%0.3f': ".3f",
                '%0.4f': ".4f",
                '%08x' : "08x",
                '%d':    "d"}.get(tformat, 'nan')

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

        if self.verbose:
            print("Found: {} <---> {}  LEN: {}".format(category, name,desired_table['@elements']))
            print(json.dumps(desired_table, indent=4, sort_keys=True))
            print("Data format: %s (from scaling table)" % self._table_format(desired_table['@scaling']))

        if desired_table['@type'] == "1D":
            print("\nTable dump\n%s\n----" % name)
            tdata = self._get_table(data_addr = desired_table['@address'], data_len = desired_table['@elements'])
            tfmt  = self._table_format(desired_table['@scaling'])
            for i in tdata:
                print("{0:{fmt}}".format(*i,fmt=tfmt))
            return

        if desired_table['@type'] == "2D":
            print("\nTable dump\n%s\n----" % name)
            tdata = self._get_table(data_addr = desired_table['@address'], data_len = desired_table['@elements'])
            tdfmt = self._table_format(desired_table['@scaling'])
            #print(json.dumps(desired_table, indent=4, sort_keys=True))
            
            if desired_table['table']['@type'] == 'X Axis':
                xdata = self._get_table(data_addr = desired_table['table']['@address'], data_len = desired_table['table']['@elements'])
                xtfmt = self._table_format(desired_table['@scaling'])
                for i in xdata:
                    print("\t{0:{fmt}}".format(i,fmt=xtfmt), end = '')
                print("")
                for i in tfmtd:
                    print("\t{0:{fmt}}".format(i,fmt=tdfmt), end = '')
                print("")
                return
            if desired_table['table']['@type'] == 'Y Axis':
                ydata = self._get_table(data_addr = desired_table['table']['@address'], data_len = desired_table['table']['@elements'])
                ytfmt = self._table_format(desired_table['@scaling'])
                for i in range(len(ydata)):
                    print(" {:<4{fmt}}".format(*ydata[i], fmt=ytfmt), end = '')
                    print(" {:<4{fmt}}".format(*tdata[i], fmt=ytfmt).ljust(5))
                return


        if desired_table['@type'] == "3D":
            print("\nTable dump\n%s\n----" % name)
            for t in desired_table['table']:
                if t['@type'] == 'X Axis':
                    xdata = self._get_table(data_addr = t['@address'], data_len = t['@elements'])
                    xtfmt = self._table_format(desired_table['@scaling'])
                if t['@type'] == 'Y Axis':
                    ydata = self._get_table(data_addr = t['@address'], data_len = t['@elements'])
                    ytfmt = self._table_format(desired_table['@scaling'])
            
            tdata = self._get_table(data_addr = desired_table['@address'], data_len = desired_table['@elements'])
            tdfmt = self._table_format(desired_table['@scaling'])

            tr_data=[]

            (toexpr,frexpr) = self._table_tofr_expr(desired_table['@scaling'])

            if self.verbose:
                print("table toexpr: {} frexpr: {}".format(toexpr,frexpr))

            if desired_table['@swapxy'] == 'true':
                #
                #print(tdata)
                for i in range(len(ydata)):
                    line=[]
                    k = i
                    for j in range(len(xdata)):
                        line.append("{:{fmt}}".format(*tdata[k], fmt = tdfmt))
                        k+=len(ydata)
                    tr_data.append(line)
            else:
                for i in range(len(ydata)):
                    line=[]
                    for j in range(len(xdata)):
                        line.append("{:{fmt}}".format(*tdata[i+j], fmt = tdfmt))
                    tr_data.append(line)
                print(tr_data)

            rjst = 9
            #print table
            print("-x-".rjust(rjst), end='')

            # x axis top
            for i in xdata:
                print("{:{fmt}}".format(*i, fmt=xtfmt).rjust(rjst), end = '')
            print("\n")
            
            z = 0
            for j in ydata:
                print("{:{fmt}} ".format(*ydata[z], fmt=ytfmt).rjust(rjst), end ='')
                a = tr_data[z]
                for l in a:
                    if toexpr == 'x':
                        print("{}".format(l).rjust(rjst), end='')
                    else:
                        #scaling table has expr - compute it
                        x = float(l)
                        expr = eval(str(toexpr))
                        print("{:{fmt}}".format(expr, fmt = tdfmt).rjust(rjst), end='')
                print("\n")
                z+=1
            return

