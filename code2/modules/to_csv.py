import csv
from datetime import datetime

from settings.settings import CSV_FOLDER


def data_to_csv(_csv, filename):

    filename = CSV_FOLDER + filename + '.csv'

    # with open(filename, 'w') as f:
    #     w = csv.DictWriter(f, _csv.keys())
    #     w.writeheader()
    #     w.writerow(_csv)


    with open(filename, "w") as csvFile:

        writer = csv.DictWriter(csvFile, _csv[0].keys())
        writer.writeheader()

        for row in _csv:
            
            line = {k: v for k, v in row.items()}
            writer.writerow(line)