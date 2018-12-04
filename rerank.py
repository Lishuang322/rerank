import numpy as np
import argparse
import os
import subprocess
def hamming_distance(s1, s2):
    return sum(ch1 != ch2 for ch1,ch2 in zip(s1,s2))

def rerank(file_r,num,code_dic,query):
#read the coarse retrieval result in the file,then find the corresponding binary code
	image_name = []
	with open(file_r,'r') as f:
		for line in f.readlines():
			line = line.strip('\n')
			image_name.append(line)
	codes = []
	sub_image = image_name[:num]
	for img in sub_image:
		#print('image: ',img)
		#print('code: ',code_dic[img])
		codes.append( code_dic[img] )


	#compute the hamming distance between query and codes
	#query = '1101101'
	#print('query:',query)
	distance = []
	for c in codes:
		distance.append( hamming_distance(query,c) )
	#print(distance)

	dis = np.array(distance)
	index = np.argsort(dis)
	rnk = np.array(sub_image)[index]
	image_name[:num] = list(rnk)
	return image_name


parser = argparse.ArgumentParser()
parser.add_argument('-c','--code',required = True,help="the path of binary code produced by ITQ")
parser.add_argument('-r','--rankedFiles',required = True,help="the dictionary of ranked files produced by image retrieval")
parser.add_argument('-l','--label',required = True,help="the path of oxford labels which contains the imfornation of query image")	
parser.add_argument('-n','--number',type=int,required =True,help="the number of images need to be reranked")
parser.add_argument('-e','--evaluate',required = True,help="path to the compute_ap to evaluate Oxford / paris")
parser.add_argument('-o','--output',required = True,help="dictionary to store reranked file ")
args = parser.parse_args()


#read the image codes into a dictionary
code_dic = {}
with open(args.code,'r') as f:
	for line in f.readlines():
		name_code = line.split()
		img_name = name_code[0].split('/')[-1]
		code_dic[img_name[:-4]] =str(name_code[1:])


file_store_query = [ ]
for fil in os.listdir(args.rankedFiles):
	if fil[-3:] == 'rnk':
		
		filename_r = args.rankedFiles + '/' +fil
		filename_q = args.label + '/' + fil[:-4] + '_query.txt'
		with open(filename_q,'r') as f:
			data_q = f.readline().split(' ')
			q_filename = data_q[0][5:]
			query = code_dic[q_filename]
			
		reranked_imgs = rerank(filename_r,args.number,code_dic,query)
	        #write result after reranking
		out_file = args.output + '/' +fil
                with open(out_file,'w') as f:
                    for i in reranked_imgs:
                        f.write(i+'\n')

#evaluate the reranked resulte
score = {} 
for result in os.listdir(args.output):
	cmd = "{0} {1}/{2} {3}/{4}".format(args.evaluate,args.label,result[:-4],args.output,result)
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	score [result[:-4]]= float(p.stdout.readlines()[0]) 
	p.wait()
for key,value in score.items():
	print ( "{0}: {1:.2f}".format(key, 100 * value) )

print ( 20 * "-" )
print ( "Mean: {0:.2f}".format(100 * np.mean(score.values())) )
	



