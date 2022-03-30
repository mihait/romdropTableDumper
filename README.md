# romdropTableDumper
Quick (and poorly coded) python 3 script that dumps tables from MX-5 NC romdrop patched ECU roms.

If you use romdrop (https://github.com/speepsio/romdrop) and want to take a quick look at one of the tables in your NC rom without opening ecuflash, this might be the right tool for you.

Required:
- this repo
- python3 ( tested on py 3.9.2 ) 
- a patched rom (like: l831ef_Rev_2xxxx.bin )
- the xml definition for the above binary (found romdrop/metada directory). l831ef.xml in this case

Usage:
- clone the repo
- edit romdumper.py
- set paths to rom and definition

````
./romdumper.py -l 
````
^^^ this will print the list of all the categories and table names available from the definition file

````
...
./romdumper.py --category 'DBW - Throttle Position Closed Limits' --table-name 'TP Closed - Default'
./romdumper.py --category 'DBW - Throttle Position Closed Limits' --table-name 'TP Closed - Max'
./romdumper.py --category 'DBW - Throttle Position Closed Limits' --table-name 'TP Closed - Min'
./romdumper.py --category 'DBW - Throttle Position Commanded Limits' --table-name 'TP Commanded Limit - Max'
./romdumper.py --category 'DBW - Throttle Position Commanded Limits' --table-name 'TP Commanded Limit - Min'
./romdumper.py --category 'DBW - Throttle Angle' --table-name 'Throttle Angle - Max'
./romdumper.py --category 'DBW - Throttle Angle' --table-name 'Throttle Angle - Conversion Multiplier'
...
````

Pick a command from above and test it:

````
./romdumper.py --category 'DBW - Throttle Position (Data Integrity)' --table-name 'APP to TP Desired - 2nd Gear'
````

Output should look like this:

````
Table dump
APP to TP Desired - 2nd Gear
----
      -x-   500.00  1000.00  1500.00  2000.00  2500.00  3000.00  4000.00  5000.00  6000.00  7000.00

    0.00      0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00

    1.50      0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00     0.00

    5.00      5.00     5.00     5.00     5.00     5.00     5.00     5.00     5.00     5.00     5.00

    7.50      7.50     7.50     7.50     7.50     7.50     7.50     7.50     7.50     7.50     7.50

   10.00     10.00    10.00    10.00    10.00    10.00    10.00    10.00    10.00    10.00    10.00

   15.00     15.00    15.00    15.00    15.00    15.00    15.00    15.00    15.00    15.00    15.00

   20.00     20.00    20.00    20.00    20.00    20.00    20.00    20.00    20.00    20.00    20.00

   25.00     25.00    25.00    25.00    25.00    25.00    25.00    25.00    25.00    25.00    25.00

   30.00     30.00    30.00    30.00    30.00    30.00    30.00    30.00    30.00    30.00    30.00

   35.00     35.00    35.00    35.00    35.00    35.00    35.00    35.00    35.00    35.00    35.00

   40.00     40.00    40.00    40.00    40.00    40.00    40.00    40.00    40.00    40.00    40.00

   45.00     45.00    45.00    45.00    45.00    45.00    45.00    45.00    45.00    45.00    45.00

   50.00     50.00    50.00    50.00    50.00    50.00    50.00    50.00    50.00    50.00    50.00

   60.00     60.00    60.00    60.00    60.00    60.00    60.00    60.00    60.00    60.00    60.00

   70.00     70.00    70.00    70.00    70.00    70.00    70.00    70.00    70.00    70.00    70.00

   80.00     80.00    80.00    80.00    80.00    80.00    80.00    80.00    80.00    80.00    80.00

   90.00     90.00    90.00    90.00    90.00    90.00    90.00    90.00    90.00    90.00    90.00

  100.00    100.00   100.00   100.00   100.00   100.00   100.00   100.00   100.00   100.00   100.00
````

Dump all tables of the rom to file:

````
./romdumper.py -a
Dumping all tables to file...
Done!

````
