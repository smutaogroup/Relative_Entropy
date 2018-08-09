#!/bin/env python
from k_shortest_paths import *  
from data_read import * 
from kl_community import *
from GirvanNewman import *


if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("Need 3 arguments.")
		print("./cmd_main.py psf dcd1 dcd2")
		sys.exit()
	
	dcd1 = sys.argv[2]; dcd2 = sys.argv[3]; psf = sys.argv[1];

	# make a directory to save data
	psf_d = psf.split('.psf')[0].split('/')[-1]
	dcd_n1 = dcd1.split('.dcd')[0].split('/')[-1]
	dcd_n2 = dcd2.split('.dcd')[0].split('/')[-1]

	os.makedirs(psf_d,exist_ok=True)

	# 1. get alpha carbon pair from psf file
	print("1. Identify alpha carbon from psf file")
	atompair = alpha_pair(psf)

	# 2. calculate distance
	print("\n2. Calculate pairwise alpha distance")
	if os.path.isfile(psf_d+"/alpha_distance.npz"):
		print("\tFind alpha distance file")
		tmp = np.load(psf_d+"/alpha_distance.npz")
		dist_dcd1 = tmp[dcd_n1]
		dist_dcd2 = tmp[dcd_n2]
	else:
		dist_dcd1 = alpha_distance(dcd1, psf, atompair) * 10 # use A as unit
		dist_dcd2 = alpha_distance(dcd2, psf, atompair) * 10 # use A as unit
		vals_to_save = {dcd_n1:dist_dcd1, dcd_n2:dist_dcd2}
		np.savez(psf_d+"/alpha_distance", **vals_to_save)

	# 3. calculate distribution for select features
	print("\n3. Estimate density distributions for each feature")
	if not os.path.isfile(psf_d+"/distribution.npy"):
		distribution_features = dcd_distribution(dist_dcd1, dist_dcd2)
		np.save(psf_d+"/distribution", distribution_features)
	else:
		print("\tFind density distributions file")
		distribution_features = np.load(psf_d+"/distribution.npy")

	# 4. calculate relative entropy regarded with each feature
	print("\n4. Calculate Relative Entropy for each residue")
	if not os.path.isfile(psf_d+"/re_matrix.npy"):
		re_matrix = relative_entropy_feature(distribution_features)
		np.save(psf_d+"/re_matrix", re_matrix)
	else:
		print("\tFind Relative Entropy file")
		re_matrix = np.load(psf_d+"/re_matrix.npy")

	# 5. build graph to identify the shortest path
	# the edge_length = 1 / relative_entropy 
	# Cutoff value 12A (0 -> no edge, distance > 12A no edge) 
	print("\n5. Build Graph")
	if not os.path.isfile(psf_d+"/graph.gpickle"):
		cutoff = input('\t Input Cutoff Value (default 12A) --> ')
		cutoff = int(cutoff) if cutoff else 12
		
		G = build_graph(distribution_features, re_matrix, cutoff)
		nx.write_gpickle(G, psf_d+"/graph.gpickle")
	else:
		print("\t Find Graph Pickle file")
		G = nx.read_gpickle(psf_d+"/graph.gpickle")

	# 6. find the longest distribution difference and identify the potential path to propagate the difference
	# find the largest relative entropy differences and corresponding nodes
	print("\n6. Calculate shortest path between source and target")
	selection = input('\t Skip or not (default skip) --> ')
	if selection:
		source = input('\t Set source (no input will calculate source based on largest relative entropy) --> ') 
		target = input('\t Set source (no input will calculate source based on largest relative entropy) --> ')
		source, target = largest_dist(re_matrix,source,target) 
		print('\t Source %d target %d' %(source, target))

		numk = input('\n\t Number of shortest path to be calculated (default 20) --> ')
		length, paths = k_shortest_paths(G, source, target, numk)
		print('\n\t Total %d Paths from %d to %d' %(len(length), source, target))

		for u,v in zip(length,paths):
			print('\t Length %.4f Nodes %s' %(u,', '.join(str(p) for p in v) ))

	# 7. find the communities 
	print("\n7. find the seperation of communities")
	algorithm = input('\t Select Algorithm \n\t\t 1. Kernighan–Lin algorithm \n\t\t 2. Girvan–Newman algorithm'+  
			'\n\t\t 3. Hybrid Algorithm (Use GirvanNewman for initial guess, then use KL to approach minimum) --> ')
	if algorithm:
		algorithm = int(algorithm)
		
		if algorithm == 1:
			communities = input('\t set the number of communities (default 2) --> ')
			repeattimes = input('\t set the minimum repeat times (default 1) --> ') 
			## best value cannot change at least 'repeattimes' value, then stop loop

			communities = int(communities) if communities else 2;
			repeattimes = int(repeattimes) if repeattimes else 1;
			best_score, final_bags = repeat_communities(re_matrix, communities, repeattimes)
			print('\t Number of Communities %d Repeat Times %d Minimum Val %.3f ' %(communities, int(repeattimes), best_score))
			for i in range(communities):
				print('\t\t Community %d \n\t\t\t Residues %s' %(i+1, ', '.join(str(p) for p in sorted(set(final_bags[i])))))
	
		elif algorithm == 2:
			result = GirvanNewman(G)
	
		elif algorithm == 3:
			print('\n\t Applied Hybrid Algorithm')
			communities = input('\t Set the number of communities (default detected by GirvanNewman Algorithm) --> ')
			
			print('\n\t Use GirvanNewman to calculate first')
			if communities:
				result = GirvanNewman(G, int(communities))
			else:
				result = GirvanNewman(G)
			
			print('\n\n\t Use Kernighan–Lin algorithm to approach minimum')
			best_score, final_bags = community(re_matrix, len(result), result) 
			print('\t Number of Communities %d Minimum Val %.3f ' %(len(final_bags), best_score))
			for i in range(len(final_bags)):
				print('\t\t Community %d \n\t\t\t Residues %s' %(i+1, ', '.join(str(p) for p in sorted(set(final_bags[i])))))

		else:
			print("\t\t Invalid Selection")
			sys.exit()



