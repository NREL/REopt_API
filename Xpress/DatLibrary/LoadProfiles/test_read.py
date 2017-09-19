filename = 'Load8760_norm_Albuquerque_FastFoodRest.dat'

f = open(filename 'r')

f.readline()

for line in f:
    print line
    print float(line.strip('\n')) * 2

print 'done'

