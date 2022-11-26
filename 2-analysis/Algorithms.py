import os
import pickle
import sys
import math
import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import networkx as nx


ALGORITHMS = [lambda x : nx.clustering(x, weight='weight'),
				lambda x : nx.pagerank(x, weight='weight'),
				lambda x: nx.closeness_vitality(x, weight='distance')]

ALGORITHM_NAMES = ['clustering',
					'pagerank',
					'closeness-vitality']


def plot_algorithms_hist(algos_dict):
	for algorithm in ALGORITHM_NAMES:
		algo_means = []
		for user_algo_values in algos_dict[algorithm].values():
			mean = np.mean(user_algo_values)
			if mean > 0:
				algo_means.append(mean)
		# bins = np.arange(0, 0.0015, 0.0001)
		# plt.hist(algo_means, bins=bins)
		plt.hist(algo_means)
		plt.savefig('../imagenes/{}-algorithm-hist.pdf'.format(algorithm))
		plt.clf()


def main():
	if '--graph-only' in sys.argv:
		algo_per_player = pickle.load(open('algorithms-per-player.pickle', 'rb'))
		plot_algorithms_hist(algo_per_player)
		return
	files_dir = os.fsencode(sys.argv[1])
	algo_per_player = {}
	listdir_ = sorted(os.listdir(files_dir))
	for idx, file_name in enumerate(listdir_):
		file_path = os.path.join(files_dir, file_name)
		if os.path.isfile(file_path) and os.fsdecode(file_name).endswith(".graphml"):
			g = nx.read_graphml(file_path).to_undirected()
			g = max(nx.connected_component_subgraphs(g), key=len)
			for u, v, d in g.edges(data=True):
				d['distance'] = 1/d['weight']
			print("Loaded batch {} of {} for algorithm calculations".format(idx + 1, len(listdir_) - 1))
			
			for idx in range(len(ALGORITHMS)):
				algo_values = ALGORITHMS[idx](g)
				existing_values = algo_per_player.get(ALGORITHM_NAMES[idx], {})
				for node in algo_values.keys():
					existing_values[node] = existing_values.get(node, []) + [algo_values[node]]
				algo_per_player[ALGORITHM_NAMES[idx]] = existing_values

	print("Finished getting algorithm results")
	with open('algorithms-per-player.pickle', 'wb') as handle:
		pickle.dump(algo_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

	plot_algorithms_hist(algo_per_player)


if __name__ == '__main__':
	main()
