import pickle
import sys
import os

import networkx as nx

def main():
	files_dir = os.fsencode(sys.argv[1])
	subdir = "startdate" if "startdate" in os.fsdecode(files_dir) else "enddate"
	listdir_ = sorted(os.listdir(files_dir))
	if not os.path.exists('data/{}/glicko-slicing-overview'.format(subdir)):
		os.makedirs('data/{}/glicko-slicing-overview'.format(subdir))
	for file_name in listdir_:
		file_path = os.path.join(files_dir, file_name)
		if os.path.isfile(file_path) and os.fsdecode(file_name).endswith('.graphml'):
			filename_suffix = '-'.join(os.fsdecode(file_name).split('-')[:2])
			print("Processing {}".format(filename_suffix))
			g = nx.read_graphml(os.fsdecode(file_path))
			if nx.is_directed(g):
				g = g.to_undirected()

			degrees = []
			for node in g.nodes:
				weightedDegree = 0
				for edge in g.edges(node):
					weightedDegree += g[edge[0]][edge[1]]['weight']
					degrees.append(weightedDegree)

			with open('data/{}/glicko-slicing-overview/degree-dist-{}.pickle'.format(subdir, filename_suffix), 'wb') as file:
				pickle.dump(degrees, file, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
	main()