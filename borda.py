import numpy as np
import argparse
import os
import subprocess
import local_rerank
from skimage import io
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary',required = True,help="directory of input voting sequence")
    parser.add_argument('--retrieval',required = True,help="directory of input voting sequence")
    parser.add_argument('-o','--output',required = True,help="dictionary to store output file ")
    parser.add_argument('-e','--evaluate',required = True,help="path to the compute_ap to evaluate Oxford / paris") 
    parser.add_argument('-l','--label',required = True,help="the path of oxford labels which contains the imfornation of query image")
    parser.add_argument('--mask',required = True,help="the mask whoes threshold equal to retrieval's")
    args = parser.parse_args()
    
    
    #step1:compute the weight

    #compute the percentage of privacy region, and store them to a dictionary
    #dataset = "/data/data-hulishuang/img-dataset/oxford_smeared/white/t155_p400/mask"
    percentage_dic = {}
    more_than_a = 0
    total = 0
    a = 0.4
    #r:a threshshod used to adjust the weight   
    r = 0.4
    for f in os.listdir(args.mask):
        file_name = os.path.join(args.mask,f)
        mask = io.imread(file_name,as_gray = True)
    
        white = np.count_nonzero(mask == 255)
        black = np.count_nonzero(mask == 0)
        percentage = np.true_divide(white,white+black)
        percentage = np.around(percentage,decimals = 2)
    
        if percentage > a:
            more_than_a = more_than_a + 1
        percentage_dic[f[:-4]] =  percentage
        total = total + 1
    percentage_more_than_a = np.true_divide(more_than_a,total)
    
    #get the query image's percentage of privacy region
    #label = "/data/data-hulishuang/img-dataset/oxford_label"
    percentage_query = {}
    for fil in os.listdir(args.label):
        if fil[-9:]=="query.txt":
        
            with open(os.path.join(args.label,fil),'r') as f:
                data_q = f.readline().split(' ')
                query_img = data_q[0][5:]
                percentage_query[fil[:-10]] = percentage_dic[query_img]
            
          
    #print(percentage_more_than_a)

    w_binary_dic ={}
    w_retrieval_dic = {}
    for key,value in percentage_query.items():
        w_binary = percentage_more_than_a * np.exp(value - r)
        w_retrieval = 1 - w_binary
        w_binary_dic[key] =  w_binary
        w_retrieval_dic[key] =  w_retrieval
    
    #print(w_binary_dic)
    #print(w_retrieval_dic)
    

      



    #step2:apply borda algorithm
    for fil in os.listdir(args.binary):
        if fil[-3:] == 'rnk':
            filename_binary = args.binary + '/' +fil
            filename_retrieval = args.retrieval + '/' +fil

            binary_rnk = local_rerank.read_rnk_as_list(filename_binary)
            retrieval_rnk = local_rerank.read_rnk_as_list(filename_retrieval)
            
            #print(retrieval_rnk)
            Points_binary = range(len(binary_rnk),0,-1)

            Points_binary = np.array(Points_binary) * w_binary_dic[fil[:-4]]

            Points_retrieval = range(len(retrieval_rnk),0,-1)

            Points_retrieval = np.array(Points_retrieval) * w_retrieval_dic[fil[:-4]]

            #record points of binary ranking list as dictionary
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

