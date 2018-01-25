#!/bin/env python
## based on Kernighan–Lin algorithm use swap and insert to approach local minimum

import numpy as np
import sys
import random
from copy import copy

def cost(bags, sim_mtx):
	tcost = 0
	for key in bags:
		curr = bags[key]
		t_len = len(curr)
		for i in range(t_len):
			for j in range(i,t_len):
				tcost += sim_mtx[curr[i]][curr[j]]
	return tcost

def insert(bags, i, j, m):
	assert m in bags[i], str(m)+' not in bags '+str(i);
	bags[i].remove(m)
	bags[j].append(m)

def swap(bags, i, j, m, n):
	assert m in bags[i], str(m)+' not in bags '+str(i);
	assert n in bags[j], str(n)+' not in bags '+str(j);
	bags[i].remove(m)
	bags[j].append(m)
	bags[j].remove(n)
	bags[i].append(n)

## third basic operation, swap one vertical in one bag, with two vertical in other bag
def swap_two(bags, i, j, k, m, n):
	assert k in bags[i], str(k)+' not in bags '+str(i);
	assert m in bags[j], str(m)+' not in bags '+str(j);
	assert n in bags[j], str(n)+' not in bags '+str(j);
	bags[i].remove(k)
	bags[j].append(k)
	bags[j].remove(m)
	bags[j].remove(n)
	bags[i].append(m)
	bags[i].append(n)


def detbags (bags, i):
	for key, values in bags.items():
		if i in values:
			return key

def remote (bags, i, bags_j, sim_mtx):
	remote_cost = 0
	for j in bags[bags_j]:
		remote_cost += sim_mtx[i][j]
	return remote_cost

def community(sim_mtx, nclusters, split=None):
	nodes = sim_mtx.shape[0]
	bags = {}
	all_node = list(range(nodes))
	random.shuffle(all_node)
	interval = nodes // nclusters
	for i in range(nclusters-1):
		bags[i] = all_node[interval*i:interval*(i+1)]
	bags[nclusters-1] = all_node[interval*(nclusters-1):]

	if split:
		for i in range(nclusters):
			bags[i] = split[i]

	while (True):
	## Calculate total cost
		total_cost_old  = cost(bags, sim_mtx)  

	## two case, each one calculate a matrix to measure the benefit and choose the maximum one until converge
	## in order to speed up calculate remote and inter cost once
		rem_loc = np.zeros((nodes, len(bags)))
		for i in range(nodes):
			for bags_j in range(len(bags)):
				rem_loc[i][bags_j] =  remote(bags, i, bags_j, sim_mtx)

		## case one: insert the vertical into other bags
		# benefit External(i, bags_m) - Internal(i, bags_i)
		insert_bene = np.zeros((nodes, len(bags)))
		for i in range(nodes):
			i_bags = detbags(bags, i)	
			for bags_j in range(len(bags)):
				insert_bene[i][bags_j] = rem_loc[i][bags_j] - rem_loc[i][i_bags]

		## case two: swap the vertical with other verticals
		swap_bene = np.zeros((nodes, nodes))
		for i in range(nodes):
			for j in range(nodes):
				i_bags = detbags(bags, i)
				j_bags = detbags(bags, j)
				if i_bags == j_bags:
					swap_bene[i][j] = 0
				else:
					swap_bene[i][j] = rem_loc[i][j_bags] + rem_loc[j][i_bags] - rem_loc[i][i_bags] - rem_loc[j][j_bags] - 2 * sim_mtx[i][j]

		
		max_insert_bene = np.min(insert_bene)
		max_swap_bene = np.min(swap_bene)	        
		
		if (max_insert_bene >= 0 and max_swap_bene >= 0):
			#print ("Reach Global Minimum:", max_insert_bene, max_swap_bene)
			break
		else:
			if (max_insert_bene <= max_swap_bene):
				#print ("Insert point Minimum: ", max_insert_bene)
				number = np.argmin(insert_bene)
				resid = number // len(bags); i_bags = detbags(bags, resid)
				target_bags = number % len(bags)
				insert(bags, i_bags, target_bags, resid);

			elif (max_swap_bene <= max_insert_bene):
				#print ("Swap two point Minimum: ", max_swap_bene)
				number = np.argmin(swap_bene)
				j_resid = number % nodes; i_resid = number // nodes
				j_bags = detbags(bags, j_resid); i_bags = detbags(bags, i_resid)
				swap(bags, i_bags, j_bags, i_resid, j_resid);

		total_cost_new  = cost(bags, sim_mtx)
		#print ("Old %.4f New %4f Total Cost New - Old %.4f" %(total_cost_old, total_cost_new, total_cost_new-total_cost_old))

	#print("Minimized Communities Total Cost %.3f" %(total_cost_new))
	#for u,v in bags.items():
	#	print("Communities %d Resides %s" %(i+1,', '.join(str(p) for p in sorted(set(v)))))
	#print(bags)

	return (total_cost_new, bags)


def repeat_communities(sim_mtx, communities, repeattimes):

	count = 0  ## the lowest minimum didn't change during last 'count' runs
	best_score = 9999;
	while(True):
		repeattimes = int(repeattimes)
		total_cost_new, bags = community(sim_mtx, communities)
		print('\t\t Count %d New score %.3f' %(count, total_cost_new))
		count += 1
		if total_cost_new < best_score - 1e-5: # accuracy is 1e-5
			best_score = total_cost_new
			final_bags = copy(bags)
			count = 0 # if lowest minimum change, then reset count
		if (count > repeattimes):
			break		
		
	final_check  = cost(final_bags, sim_mtx)
	np.testing.assert_almost_equal(final_check, best_score, decimal=5, 
	err_msg='Final Check not equal best', verbose=True)

	return (best_score, final_bags)

