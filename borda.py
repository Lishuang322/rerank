import numpy as np
import argparse
import os
import subprocess
import local_rerank
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary',required = True,help="directory of input voting sequence")
    parser.add_argument('--retrieval',required = True,help="directory of input voting sequence")
    parser.add_argument('-o','--output',required = True,help="dictionary to store output file ")
    parser.add_argument('-e','--evaluate',required = True,help="path to the compute_ap to evaluate Oxford / paris") 
    parser.add_argument('-l','--label',required = True,help="the path of oxford labels which contains the imfornation of query image")   
    args = parser.parse_args()
    w = 0.4
    for fil in os.listdir(args.binary):
        if fil[-3:] == 'rnk':
            filename_binary = args.binary + '/' +fil
            filename_retrieval = args.retrieval + '/' +fil

            binary_rnk = local_rerank.read_rnk_as_list(filename_binary)
            retrieval_rnk = local_rerank.read_rnk_as_list(filename_retrieval)
            
            #print(retrieval_rnk)
            Points_binary = range(len(binary_rnk),0,-1)
            Points_binary = np.array(Points_binary) * (1-w)
            Points_retrieval = range(len(retrieval_rnk),0,-1)
            Points_retrieval = np.array(Points_retrieval) * w
            #record points os binary ranking list as dictionary
            binary_points_dic = {}
            for i in range(len(binary_rnk)):
                binary_points_dic[ binary_rnk[i] ] = Points_binary[i]

            #add two list
            for i in range(len(retrieval_rnk)):
                Points_retrieval[i] = Points_retrieval[i] + binary_points_dic[ retrieval_rnk[i] ]
                #print(Points[i])            
            #sort
            index = np.argsort(-np.array(Points_retrieval),kind = 'mergesort')
            combine = np.array(retrieval_rnk)[index]
            #write
            out_file = args.output + '/' +fil
            with open(out_file,'w') as f:
                for i in combine:
                    f.write(i+'\n')
    #evaluate the reranked resulte
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

