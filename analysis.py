import os
import rerank
import argparse
def load_as_set (fil_name):
    with open (fil_name,'r') as f:
        s = set()
        for line in f.readlines():
            s.add(line.strip('\n'))
            
    return s

def get_pos_and_neg_set(lab_dir,query_id):
    #find the corresponding label file
    lab_good = lab_dir + '/' + query_id + '_good.txt'
    lab_ok = lab_dir + '/' + query_id + '_ok.txt'
    lab_junk = lab_dir + '/' + query_id + '_junk.txt'
    #load label as set
    good = load_as_set(lab_good)
    ok = load_as_set(lab_ok)
    junk = load_as_set(lab_junk)
    pos = good | ok
    return pos , junk
    
    
parser = argparse.ArgumentParser()
parser.add_argument('-c','--code',required = True,help="the path of binary code produced by ITQ")
parser.add_argument('-f','--file',required = True,help = 'ranked file for analysising')
parser.add_argument('-l','--label',required = True, help = 'directory of image labels' )
parser.add_argument('-o','--output',required =True,help = 'output directory')
args = parser.parse_args()


 
code_dic = rerank.code_dictory(args.code)
query_id = args.file.split('/')[-1][:-4]
query_image = rerank.get_query_img(args.label,query_id) 
query =  code_dic[query_image]
images = rerank.read_rnk_as_list(args.file)
codes = rerank.map_img_to_codes(images,code_dic) 
#compute the hamming distance between query and codes
distance = []
for c in codes:
    distance.append( rerank.hamming_distance(query,c) ) 
    
pos,neg = get_pos_and_neg_set(args.label,query_id)    
    

#make a log directory 
log_dir = args.output + '/' + 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
#write a log file to analysis
log_f = log_dir +'/' + query_id
with open(log_f,'w') as f:
    for i in range(len(images)):
        if images[i] in pos:
            f.write(images[i]+' '+str(distance[i])+' p'+'\n')
        elif images[i] in neg:
            f.write(images[i]+' '+str(distance[i])+' n'+'\n')
        else:
            f.write(images[i]+' '+str(distance[i])+'\n')