#!/bin/env python
# Thanks for Guilherme Maia https://gist.github.com/guilhermemm/d4623c574d4bccb6bf0c implementations for k_shortest_paths! 
import networkx as nx
from heapq import heappush, heappop
from itertools import count
import numpy as np

def largest_dist(re_matrix, source=None, target=None):
	if not (source or target):
		nmax = np.argmax(re_matrix)
		return (nmax // re_matrix.shape[0], nmax % re_matrix.shape[0])
	elif source and (not target):
		source = int(source)
		target = np.argmax(re_matrix[source])
		return (source, target)
	elif target and (not source):
		target = int(target)
		source = np.argmax(re_matrix[:,target])
		return (source, target)
	else:
		source = int(source)
		target = int(target)
		return (source, target)

def k_shortest_paths(G, source, target, k):
	k = int(k) if k else 20
	
	# G: networkx graph
	# source, target: should be one of G nodes
	assert source in G.nodes(), "No source "+str(source)+" in graph"
	assert target in G.nodes(), "No target "+str(target)+" in graph"

	if source == target:
		return ([0], [[source]]) 
	
	length, path = nx.single_source_dijkstra(G, source, weight='length')
	if target not in length:
		raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))
	
	lengths = [length[target]]
	paths = [path[target]]

	c = count()
	B = []
	G_original = G.copy()

	for i in range(1, k):
		# for Ak iteration
		for j in range(len(paths[-1]) - 1):
			# iterate the spur_node, and the root_path in Ak-1 path
			# remove all the edges the spur nodes direct connected to (save all attr in edges_removed) in Ak-1 paths
			spur_node = paths[-1][j]
			root_path = paths[-1][:j + 1]
			edges_removed = []
			for c_path in paths:
				if len(c_path) > j and root_path == c_path[:j + 1]:
					u = c_path[j]
					v = c_path[j + 1]
					if G.has_edge(u, v):
						edge_attr = G[u][v]
						G.remove_edge(u, v)
						edges_removed.append((u, v, edge_attr))

			# remove all the edges in the root path (avoid circular) 
			for n in range(len(root_path) - 1):
				node = root_path[n]
				edges =  list(G.edges(node, data=True))
				for u, v, edge_attr in edges:
					G.remove_edge(u, v)
					edges_removed.append((u, v, edge_attr))

			# calculate the spur node to target length
			spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, weight='length') 
			
			# if spur node can connect to target with removing all the edges in Ak, then save all the spur path
			if target in spur_path and spur_path[target]:
				total_path = root_path[:-1] + spur_path[target]
				total_path_length = get_path_length(G_original, root_path) + spur_path_length[target]
				heappush(B, (total_path_length, next(c), total_path)) # always put the length small at the top

			
			# update all the removed edges
			for e in edges_removed:
				u, v, edge_attr = e
				G.add_edge(u, v, length=edge_attr['length'])

		# for each iteration, add all paths founded.
		if B:
			(l, _, p) = heappop(B) # B already sorted based on cost, the shortst length will pop out as Ak
			lengths.append(l)
			paths.append(p)
		else:
			break

	return (lengths, paths)


def get_path_length(G, path):
	length = 0
	if len(path) > 1:
		for i in range(len(path) - 1):
			u = path[i]
			v = path[i + 1]

			length += G[u][v].get('length')

	return length    

