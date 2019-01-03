import numpy as np
import argparse
import os
import subprocess
def code_dictory (itq_file):
    code_dic = {}
    with open(itq_file,'r') as f:
        for line in f.readlines():
            name_code = line.split()
            #img_name = name_code[0].split('/')[-1]
            img_name = name_code[0]
            code_dic[img_name[:-4]] =str(name_code[1:])
    return code_dic
def hamming_distance(s1, s2):
    return sum(ch1 != ch2 for ch1,ch2 in zip(s1,s2))

    
    
def map_img_to_codes (images,code_dic):
    codes = []
    for i in range(len(images)):
        img = images[i]
        if code_dic.has_key(img):
            codes.append( code_dic[img] )
        else:
            #if the img doesn't have binary code, previous code is img's code
            codes.append(codes[-1])
        #print(img + ': ' + codes[i])
    return codes
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--code',required = True,help="the path of binary code produced by ITQ")
    parser.add_argument('-l','--label',required = True,help="the directory of labels which contains the imfornation of query image")	
    parser.add_argument('-e','--evaluate',required = True,help="path to the compute_ap to evaluate Oxford / paris")
    parser.add_argument('-o','--output',required = True,help="dictionary to store reranked file ")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output) 
    #read the image codes into a dictionary
    code_dic = code_dictory(args.code)
    
    #get images ,store them as list
    images = code_dic.keys()
    
    codes = map_img_to_codes(images,code_dic)
   




    #for every query,compute their similar images
    for query_file in os.listdir(args.label):
        
        if query_file[-9:] == 'query.txt':
            #print(query_file)
            #get query image
            with open(os.path.join(args.label,query_file),'r') as f:
                data_q = f.readline().split(' ')
                query_img = data_q[0][5:] if data_q[0].startswith('oxc1_') else data_q[0]
            query = code_dic[query_img]
            #print(query)
            #compute the hamming distance between query and codes
            distance = []
            for c in codes:
                distance.append( hamming_distance(query,c) )
            dis = np.array(distance)
            index = np.argsort(dis,kind = 'mergesort')
            rnk = np.array(images)[index]
            #write result to file
            out_file = args.output + '/' +query_file[:-10] + '.rnk'
            with open(out_file,'w') as f:
                for i in rnk:
                    f.write(i+'\n')
                    
                    
    
    score = {}
    for result in os.listdir(args.output):
        if result[-3:] != 'rnk':
            continue
        
        cmd = "{0} {1}/{2} {3}/{4}".format(args.evaluate,args.label,result[:-4],args.output,result)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        score [result[:-4]]= float(p.stdout.readlines()[0]) 
        p.wait()
    print('\n')   
    for key,value in score.items():
        print ( "{0}: {1:.2f}".format(key, 100 * value) )
            
    print ( 20 * "-" )
    print ( "Mean: {0:.2f}".format(100 * np.mean(score.values())) )




