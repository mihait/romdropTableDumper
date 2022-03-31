# romdropTableDumper
Quick (and poorly coded) python 3 script that dumps tables from MX-5 NC romdrop patched ECU roms.

If you use romdrop (https://github.com/speepsio/romdrop) and want to take a quick look at one of the tables in your NC rom without opening ecuflash, this might be the right tool for you.

## Required:
- this repo
- python3 ( tested on py 3.9.2 ) 
- a patched rom (like: l831ef_Rev_2xxxx.bin ) BINARY ONLY  ( NOT .SRF )
- the xml definition for the above binary (found romdrop/metada directory). l831ef.xml in this case

## Configuration:
- clone the repo
- edit romdumper.py
- set paths to rom and definition

## Usage:
````
usage: romdumper.py [-h] {list-all,dump-table,dump-all,cli-dump-all} ...

romdrop table(s) dumper

positional arguments:
  {list-all,dump-table,dump-all,cli-dump-all}
                        sub-command help
    list-all            list all tables
    dump-table          dump one table by category and name
    dump-all            dump all tables using the rom/def/output files defined inside the script
    cli-dump-all        dump all tables to file using command line specified parameters for rom/def/outfile

optional arguments:
  -h, --help            show this help message and exit
````


#### List all categories and tables

````
./romdumper.py list-all
````

Output:
````
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - Non Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 1st Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 2nd Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 3rd Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 4th Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 5th Gear'
./romdumper.py dump-table -c 'DBW - Cruise Control' -n 'CC Sensitivity - 6th Gear'
... and so on ...
````


#### Pick a command from above and test it:

````
./romdumper.py dump-table -c 'Spark Idle Limit' -n 'Spark Idle Limit '
````

Output should look like this:

````
Table dump
Spark Idle Limit 
----
      -x-    0.125    0.188    0.250    0.312    0.375    0.438    0.500    0.562    0.625

     500      5.50     5.50     5.00     4.00    -2.50    -6.00    -7.50   -10.50   -14.10

     600      6.00     6.00     5.50     5.00    -1.00    -5.00    -6.00    -9.00   -12.50

     700      8.00     8.00     8.00     6.00     0.00    -2.00    -4.00    -7.50   -11.00

     800      8.00     8.00     8.00     7.00     2.00     1.00    -2.00    -6.00    -9.50

     900      8.00     8.00     8.00     8.00     3.50     2.00     0.00    -3.00    -6.00

    1000     12.00    12.00    12.00     9.00     5.00     3.00     1.00     0.00    -2.00

    1100     14.00    14.00    13.00    10.00     6.00     4.00     2.00     1.00    -1.00

    1200     16.00    16.00    14.00    11.00    10.00     8.00     6.00     5.00     3.50

    1300     18.00    18.00    15.00    12.00    11.00     9.00     7.00     6.00     5.00

    1400     18.50    18.50    15.50    13.00    11.50     9.50     8.00     7.00     6.00

    1500     19.00    19.00    16.00    14.00    12.00    10.00     9.00     8.00     7.00


````


#### Dump all tables of the rom to file:

````
./romdumper.py dump-all
Dumping all tables to file...
Done!
````

#### Dump all tables (all parameters specified from cli):

````
./romdumper.py cli-dump-all -r roms/L831EG_Rev_xyz.bin -d metadata/l831eg.xml -o l831eg-ver-xyz-dump.txt
Dumping all tables to file...
Done!
````

#### How to see what's changed between two roms ? 

````
pip install diffoscope
````


````
diffoscope \
	--max-report-size 0 \
	--no-default-limits \
	--max-diff-block-lines 0 \
	dumps/L831EG_Rev_xxx0.TXT \
	dumps/L831EG_Rev_xxx31.TXT \
	--html-dir html/v0_to_v31/
````

Don't worry, diffoscope will create the output directory for you.

Browse to the above directory and open index.html in your favorite browser.
Click ... Open expanded diff ... at the bottom of the page.

Adjust page zoom if necessary!

