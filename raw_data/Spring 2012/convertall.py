#! python

import os
from xlsx2csv.xlsx2csv import xlsx2csv

for fname in os.listdir('.'):
    if fname.endswith('.xlsx'):
        out_name = fname.rsplit('.', 1)[0] + '.csv'
        with open(out_name, 'w') as outfile:
            xlsx2csv(fname, outfile)
