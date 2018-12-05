#analysis the log file
import argparse

def load (fil_name):
    with open (fil_name,'r') as f:
        s = set()
        for line in f.readlines():
            s.add(line.strip('\n'))
            
    return s

parser = argparse.ArgumentParser()
parser.add_argument('-f','--file',required = True,help = 'log file for analysising')
parser.add_argument('-l','--label',required = True, help = 'directory of image labels' )
args = parser.parse_args()

#find the corresponding label file
query_file_name = args.file.split('/')[-1][:-4]
lab_good = args.label + '/' +query_file_name + '_good.txt'
lab_ok = args.label + '/' +query_file_name + '_ok.txt'
lab_junk = args.label + '/' +query_file_name + '_junk.txt'

#load label as set
good = load(lab_good)
ok = load(lab_ok)
junk = load(lab_junk)
pos = good | ok
#print('pos size:' + str(len(pos)))
#print('junk size:' + str(len(junk)))

#label images with p (positive) or n (negative)  
with open (args.file,'r') as f:
    lines = f.readlines()
    count_pos = 0
    count_junk = 0
    for i in range (len(lines)):
        lines[i] = lines[i].strip('\n')
        img_name = lines[i].split(' ')[0]
        if img_name in pos:
            count_pos = count_pos + 1
            lines[i] = lines[i] + ' ' + 'p'
            #print(lines[i])
        elif img_name in junk:
            count_junk = count_junk + 1
            lines[i] = lines[i] + ' ' + 'n' 
            
    #print('pos: ' + str(count_pos))
    #print('junk: ' + str(count_junk))
for line in lines:
    dis = line.split(' ')[1]
    if int(dis) <=100:
        print (line + '\n')

#write analysis result
''' 
out_file = args.file[:-4] + '.ana'
with open(out_file,'w') as f:
    for line in lines:
        line = line + '\n'
        f.write(line)
'''