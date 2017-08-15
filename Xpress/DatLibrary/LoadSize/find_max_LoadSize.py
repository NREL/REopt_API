import os

with open(os.path.join('..', 'annual_loads.csv'), 'w') as fo:
    fo.write("city,bldg,annual_load(kWh),\n")

    dat_list = os.listdir('.')
    load_list=[]

    for dat in dat_list:
        city_bldg = dat[9:-4]
        city = city_bldg[:city_bldg.find('_')]
        bldg = city_bldg[len(city)+1:]

        with open(dat,'r') as f:

            for i,line in enumerate(f):
                if i == 1:
                    s = str(line).strip("\t,\r\n")
                    try:
                        load_list.append(float(s))
                        if bldg != "FlatLoad":
                            fo.write(city+","+bldg+","+s+",\n")
                    except:
                        print 'could not convert ', s, ' in file ', dat


# load_list = [float(ld) for ld in open(dat_list).readline()]

print len(load_list)
print max(load_list)