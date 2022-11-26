import sys
import os

import networkx as nx
import matplotlib.pyplot as plt

def main():
	files_dir = os.fsencode(sys.argv[1])
	listdir_ = sorted(os.listdir(files_dir))
	graph_sizes = []
	num_of_edges = []
	for file_name in listdir_:
		file_path = os.path.join(files_dir, file_name)
		if os.path.isfile(file_path) and os.fsdecode(file_name).endswith('.graphml'):
			g = nx.read_graphml(os.fsdecode(file_path))
			graph_sizes.append(g.size())
			current_num_edges = 0
			for (black, white, weight) in g.edges.data('weight', default=1):
				current_num_edges += weight
			num_of_edges.append(current_num_edges)

	if not os.path.exists('imagenes'):
		os.makedirs('imagenes')

	plt.plot(graph_sizes)
	plt.savefig('imagenes/graph-size-evolution.pdf')
	plt.clf()

	plt.plot(num_of_edges)
	plt.savefig('imagenes/graph-edges-evolution.pdf')
	plt.clf()

if __name__ == '__main__':
	main()