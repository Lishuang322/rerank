import numpy as np
import argparse
import os
import subprocess
def code_dictory (itq_file):
    code_dic = {}
    with open(itq_file,'r') as f:
        for line in f.readlines():
            name_code = line.split()
            img_name = name_code[0].split('/')[-1]
            code_dic[img_name[:-4]] =str(name_code[1:])
    return code_dic
def hamming_distance(s1, s2):
    return sum(ch1 != ch2 for ch1,ch2 in zip(s1,s2))

def read_rnk_as_list(file_rnk):
    image_name = []
    with open(file_rnk,'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            image_name.append(line)
    return image_name
    
    
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
        
def rerank(image_name,num,code_dic,query):
    #read the coarse retrieval result in the file,then find the corresponding binary code
    print('query: '+query)
    sub_image = image_name[:num]
    codes = map_img_to_codes(sub_image,code_dic)
          
    #compute the hamming distance between query and codes
    distance = []
    for c in codes:
        distance.append( hamming_distance(query,c) )
    #print('distance: ')
    #print(distance)
    dis = np.array(distance)
    index = np.argsort(dis,kind = 'mergesort')
    rnk = np.array(sub_image)[index]
    image_name[:num] = list(rnk)
    return image_name
    
def get_query_img (dic_label,query_id):
    query_file = dic_label + '/' + query_id + '_query.txt'
    with open(query_file,'r') as f:
        data_q = f.readline().split(' ')
        query_img = data_q[0][5:]
    return query_img

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--code',required = True,help="the path of binary code produced by ITQ")
    parser.add_argument('-r','--rankedFiles',required = True,help="the dictionary of ranked files produced by image retrieval")
    parser.add_argument('-l','--label',required = True,help="the path of oxford labels which contains the imfornation of query image")	
    parser.add_argument('-n','--number',type=int,required =True,help="the number of images need to be reranked")
    parser.add_argument('-e','--evaluate',required = True,help="path to the compute_ap to evaluate Oxford / paris")
    parser.add_argument('-o','--output',required = True,help="dictionary to store reranked file ")
    args = parser.parse_args()


    #read the image codes into a dictionary
    code_dic = code_dictory(args.code)



    for fil in os.listdir(args.rankedFiles):
        if fil[-3:] == 'rnk':
            filename_r = args.rankedFiles + '/' +fil
            #get query image
            query_image = get_query_img(args.label,fil[:-4])        
            query = code_dic[query_image]
            #get image list
            images_list = read_rnk_as_list(filename_r)
            reranked_imgs = rerank(images_list,args.number,code_dic,query)
            #write result after reranking
            #this result is for evaluate 
            out_file = args.output + '/' +fil
            with open(out_file,'w') as f:
                for i in reranked_imgs:
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
        for key,value in score.items():
            print ( "{0}: {1:.2f}".format(key, 100 * value) )
            
            print ( 20 * "-" )
            print ( "Mean: {0:.2f}".format(100 * np.mean(score.values())) )




