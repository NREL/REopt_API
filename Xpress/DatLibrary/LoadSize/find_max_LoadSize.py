import os

dat_list = os.listdir('.')
load_list=[]
for dat in dat_list:
    with open(dat,'r') as f:
        for i,line in enumerate(f):
            if i == 1:
                s = str(line).strip("\t \n ,")
                try:
                    load_list.append(float(s))
                except:
                    print 'could not convert ', s, ' in file ', dat
# load_list = [float(ld) for ld in open(dat_list).readline()]

print len(load_list)
print max(load_list)