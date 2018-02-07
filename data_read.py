#!/bin/env python
import numpy as np
import mdtraj as md
import sys
from sklearn.neighbors import KernelDensity
import os
import networkx as nx

def alpha_pair(psf):
	alpha_carbon_number = []
	for i in open(psf):
		l = i.split()
		if len(l) == 11:
			if l[4] == 'CA':
				alpha_carbon_number.append(int(l[0]))

	num=len(alpha_carbon_number)

	atompair=[]
	for i in range(num):
		for j in range(i+1,num):
			atompair += [[alpha_carbon_number[i],alpha_carbon_number[j]]]

	return atompair

def alpha_distance(dcd, psf, atompair):
	traj = md.load_dcd(dcd, psf)
	distance = md.compute_distances(traj, atompair)
	return distance

def dcd_distribution(dcd1,dcd2):
	# assume dcd1, dcd2 is the alpha carbon distance
	num_features = dcd1.shape[1]
	distribution_features = np.zeros((num_features,3,500)) ## 500 is the distribution resolution
	for i in range(num_features):
		distribution_features[i] = distribution(dcd1[:,i], dcd2[:,i]) 
	return distribution_features

def distribution(dcd1_f1, dcd2_f1):
	# assume dcd1_f1, dcd2_f1 is the features already got from dcd1 and dcd2 distance
	minx = min(min(dcd1_f1), min(dcd2_f1))
	maxx = max(max(dcd1_f1), max(dcd2_f1))
	dcd1_f1 = dcd1_f1[:, np.newaxis]; dcd2_f1 = dcd2_f1[:, np.newaxis]
	xs = np.linspace(minx,maxx,500)[:, np.newaxis]
	kde1 = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(dcd1_f1)
	kde2 = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(dcd2_f1)
	log_dens1 = np.exp(kde1.score_samples(xs)); log_dens1 = log_dens1 / np.sum(log_dens1);
	log_dens2 = np.exp(kde2.score_samples(xs)); log_dens2 = log_dens2 / np.sum(log_dens2);
	
	return ([xs.transpose()[0], log_dens1, log_dens2])

def entropy(d1,d2):
	# suppose d1, d2 is the distribution density for feature1, feature2
	d2[d2 < 1e-7] = 1e-7; ## make sure not divide by 0
	vec = np.zeros(len(d1))
	for i in range(len(d1)):
		if d1[i] == 0:
			vec[i] = 0
		else:
			vec[i] = d1[i]*np.log(d1[i]/d2[i])
	return np.sum(vec) 

def relative_entropy_feature(distribution_features):
	# suppose dcd1_dist, dcd2_dist are the results contain all the distributions
	num_features = distribution_features.shape[0]
	relative_features = np.zeros(num_features)
	for i in range(num_features):
		relative_features[i] = (entropy(distribution_features[i][1], distribution_features[i][2]) + 
		entropy(distribution_features[i][2], distribution_features[i][1]))/2
	
	num_resid = int(np.sqrt(num_features*2 + 1.0/4) + 1.0/2)
	re_matrix = np.zeros((num_resid,num_resid))
	count = 0
	for i in range(num_resid):
		for j in range(i+1,num_resid):
			re_matrix[i][j] = relative_features[count]
			re_matrix[j][i] = relative_features[count]
			count = count + 1

	return re_matrix

def build_graph(distribution_features, re_matrix, cutoff):
	g = nx.Graph()
	num_nodes = re_matrix.shape[0]
	g.add_nodes_from(np.arange(num_nodes).astype(int))
	
	fe = 0 # for feature index in distribution_features
	for i in range(num_nodes):
		for j in range(i+1, num_nodes):
			if ((re_matrix[i][j] != 0) and   
				(distribution_features[fe][0][np.argmax(distribution_features[fe][1])] < cutoff and 
				distribution_features[fe][0][np.argmax(distribution_features[fe][2])] < cutoff)):
				# only when i,j relative entropy is not 0 and maximum distribution distance less than cutoff value
				g.add_edge(i,j,length=(1.0/re_matrix[i][j]))
			fe += 1
	return g
