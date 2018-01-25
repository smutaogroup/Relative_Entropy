#!/bin/env python
import networkx as nx


def CmtyGirvanNewmanStep(G):
	init_ncomp = nx.number_connected_components(G)
	ncomp = init_ncomp
	while ncomp <= init_ncomp:
		bw = nx.edge_betweenness_centrality(G, weight='length')
		max_ = max(bw.values())
		for k, v in bw.items():
			if float(v) == max_:
				G.remove_edge(k[0],k[1])
		ncomp = nx.number_connected_components(G)

def GirvanNewmanGetModularity(G, deg_, m_):
	New_A = nx.adj_matrix(G)
	New_deg = {}
	New_deg = UpdateDeg(New_A, list(G.nodes()))
	comps = nx.connected_components(G)
	print('\t\t No of communities in decomposed G: %d' %(nx.number_connected_components(G)))
	Mod = 0
	for c in comps:
		EWC = 0 # no of edges wthin a comunities
		RE = 0 # no of random egdes
		for u in c:
			EWC += New_deg[u]
			RE += deg_[u]
		Mod += ( float(EWC) - float(RE*RE)/float(2*m_) )
	Mod = Mod/float(2*m_)
	return Mod

def runGirvanNewman(G, Orig_deg, m_, communities):
	BestQ = 0.0
	Q = 0.0
	while True:
		CmtyGirvanNewmanStep(G)
		Q = GirvanNewmanGetModularity(G, Orig_deg, m_);
		print("\t\t Modularity of decomposed G: %f" % (Q))
		if communities:
			if (nx.number_connected_components(G) == communities):
				Bestcomps = nx.connected_components(G)
				result = sorted(Bestcomps, key = len, reverse=True)
				result = [sorted(i) for i in result]
				print ("\n\t\t ############ RESULT #############")
				print ("\t\t\t Graph communities:  ", result)
				return result
		
		if Q > BestQ:
			BestQ = Q
			Bestcomps = nx.connected_components(G)  #Best Split
			result = sorted(Bestcomps, key = len, reverse=True)
		if G.number_of_edges() == 0:
			break

	if BestQ > 0.0:
		print ("\n\t\t ############ RESULT #############")
		print ("\t\t\t No of communities in decomposed G: %d" %(len(result)))
		print ("\t\t\t Max modularity (Q): %f" % (BestQ))
		result = [sorted(i) for i in result]
		print ("\t\t\t Graph communities:  ", result)
		return result
		
	else:
		print ("\t\t Max modularity (Q): %f" % (BestQ))

def UpdateDeg(A, nodes):
	deg_dict = {}
	n = len(nodes)
	B = A.sum(axis = 1)
	for i in range(n):
		deg_dict[nodes[i]] = B[i, 0]
	return deg_dict


def GirvanNewman(G, communities=None): 
	n = G.number_of_nodes()
	A = nx.adj_matrix(G)
	m_ = 0.0
	for i in range(0,n):
		for j in range(0,n):
			m_ += A[i,j]

	m_ = m_/2.0
	Orig_deg = {}
	Orig_deg = UpdateDeg(A, list(G.nodes()))

	result = runGirvanNewman(G, Orig_deg, m_, communities)
	return result
