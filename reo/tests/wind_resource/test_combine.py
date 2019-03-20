import csv
import os

file1 = "39.91065_-105.2348_windtoolkit_2012_60min_40m.srw"
file2 = "39.91065_-105.2348_windtoolkit_2012_60min_60m.srw"
file_out = "39.91065_-105.2348_windtoolkit_2012_60min_40m_60m.srw"

file_resource_heights = {40: file1, 60: file2}
heights = [40, 60]

# currently only available for hourly data
if len(heights) > 1:
    data = [None] * 2
    for height, f in file_resource_heights.iteritems():
        if os.path.isfile(f):
            with open(f) as file_in:
                csv_reader = csv.reader(file_in, delimiter=',')
                line = 0
                for row in csv_reader:
                    if line < 2:
                        data[line] = row
                    else:
                        if line >= len(data):
                            data.append(row)
                        else:
                            data[line] += row
                    line += 1

    with open(file_out, 'w') as fo:
        writer = csv.writer(fo)
        writer.writerows(data)

