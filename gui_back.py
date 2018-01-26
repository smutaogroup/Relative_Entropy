#!/bin/env python
from k_shortest_paths import *  
from data_read import * 
from kl_community import *
from GirvanNewman import *

def background_call(psf_full,dcd1_full,dcd2_full,reuse_alphadist,reuse_densdist,reuse_re,reuse_graph,cutoff,source,target,selectalgrithm,commu,repeat): 
	
	psf  = psf_full.split('/')[-1]
	dcd1 = dcd1_full.split('/')[-1]
	dcd2 = dcd2_full.split('/')[-1]

	# make a directory to save data
	os.makedirs(psf.split('.')[0],exist_ok=True)
	logfile = open(psf.split('.')[0]+'/logfile.txt','w')
	
	atompair = alpha_pair(psf_full)

	# 2. calculate distance
	if reuse_alphadist == 1 and os.path.isfile(psf.split('.')[0]+"/alpha_distance.npz"):
		tmp = np.load(psf.split('.')[0]+"/alpha_distance.npz")
		dist_dcd1 = tmp[dcd1.split('.')[0]]
		dist_dcd2 = tmp[dcd2.split('.')[0]]
	else:
		dist_dcd1 = alpha_distance(dcd1_full, psf_full, atompair) * 10 # use A as unit
		dist_dcd2 = alpha_distance(dcd2_full, psf_full, atompair) * 10 # use A as unit
		vals_to_save = {dcd1.split('.')[0]:dist_dcd1, dcd2.split('.')[0]:dist_dcd2}
		np.savez(psf.split('.')[0]+"/alpha_distance", **vals_to_save)

	# 3. calculate distribution for select features
	if reuse_densdist == 0 or (not os.path.isfile(psf.split('.')[0]+"/distribution.npy")):
		distribution_features = dcd_distribution(dist_dcd1, dist_dcd2)
		np.save(psf.split('.')[0]+"/distribution", distribution_features)
	else:
		distribution_features = np.load(psf.split('.')[0]+"/distribution.npy")

	# 4. calculate relative entropy regarded with each feature
	if reuse_re == 0 or (not os.path.isfile(psf.split('.')[0]+"/re_matrix.npy")):
		re_matrix = relative_entropy_feature(distribution_features)
		np.save(psf.split('.')[0]+"/re_matrix", re_matrix)
	else:
		re_matrix = np.load(psf.split('.')[0]+"/re_matrix.npy")

	# 5. build graph to identify the shortest path
	# the edge_length = 1 / relative_entropy 
	# Cutoff value 12A (0 -> no edge, distance > 12A no edge) 
	if reuse_graph == 0 or (not os.path.isfile(psf.split('.')[0]+"/graph.gpickle")):
		cutoff = int(cutoff)
		G = build_graph(distribution_features, re_matrix, cutoff)
		nx.write_gpickle(G, psf.split('.')[0]+"/graph.gpickle")
	else:
		G = nx.read_gpickle(psf.split('.')[0]+"/graph.gpickle")

	# 6. find the longest distribution difference and identify the potential path to propagate the difference
	# find the largest relative entropy differences and corresponding nodes
	logfile.write("\nCalculate shortest path between source and target\n")	

	source, target = largest_dist(re_matrix,source,target) 
	logfile.write('\t Source %d target %d\n' %(source, target))

	length, paths = k_shortest_paths(G, source, target, 50)
	logfile.write('\n\t Total %d Paths from %d to %d\n' %(len(length), source, target))

	for u,v in zip(length,paths):
		logfile.write('\t Length %.4f Nodes %s\n' %(u,', '.join(str(p) for p in v) ))

	# 7. find the communities 
	logfile.write("\nFind the seperation of communities use Algorithm %d \n" %(selectalgrithm))

	if selectalgrithm == 1:
		commu = int(commu)
		repeat = int(repeat)
		best_score, final_bags = repeat_communities(re_matrix, commu, repeat)
		logfile.write('\t Number of Communities %d Repeat Times %d Minimum Val %.3f \n' %(commu, repeat, best_score))
		for i in range(commu):
			logfile.write('\t\t Community %d \n\t\t\t Residues %s \n' %(i+1, ', '.join(str(p) for p in sorted(set(final_bags[i])))))

	elif selectalgrithm == 2:
		result = GirvanNewman(G)
		best_score, final_bags = community(re_matrix, len(result), result)
		logfile.write('\t Number of Communities %d Minimum Val %.3f \n' %(len(final_bags), best_score))
		for i in range(len(final_bags)):
			logfile.write('\t\t Community %d \n\t\t\t Residues %s\n' %(i+1, ', '.join(str(p) for p in sorted(set(final_bags[i])))))

	elif selectalgrithm == 3:
		if commu:
			commu = int(commu)
			result = GirvanNewman(G, commu)
		else:
			result = GirvanNewman(G)
		
		logfile.write('\n\n\t Use Kernighan–Lin algorithm to approach minimum\n')
		best_score, final_bags = community(re_matrix, len(result), result) 
		logfile.write('\t Number of Communities %d Minimum Val %.3f \n' %(len(final_bags), best_score))
		for i in range(len(final_bags)):
			logfile.write('\t\t Community %d \n\t\t\t Residues %s\n' %(i+1, ', '.join(str(p) for p in sorted(set(final_bags[i])))))

	logfile.close()
