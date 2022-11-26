import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import pickle
import datetime

def getLineStyle(dirname):
	if dirname == 'oneweek':
		return '--'
	elif dirname == 'overlapping':
		return '-'
	elif dirname == 'onemonth':
		return ':'
	else:
		return None

def main():
	root_files_dir = os.fsencode(sys.argv[1]) # neo4j/new-import/(startdate\enddate)/playersonly
	pickle_dir = 'startdate' if 'startdate' in os.fsdecode(root_files_dir) else 'enddate'
	fig, plots = plt.subplots(4, sharex=True)

	if '--graph-only' in sys.argv:
		for dirname in ['oneweek', 'overlapping', 'onemonth']:
			previously_calculated_values = pickle.load(open('data/{}/{}-duncan-watts-values-updated.pickle'.format(pickle_dir, dirname), 'rb'))
			plotAllPlots(previously_calculated_values, plots, getLineStyle(dirname))
		plt.savefig('imagenes/{}/test-duncan-watts-metrics.pdf'.format(pickle_dir))
		return

	for dirname in ['oneweek', 'overlapping', 'onemonth']:
		windowDates = []
		def getDate(filename):
			parsedDate = datetime.datetime.strptime(filename.decode().split('-')[1], "%Y%m%d").date()
			windowDates.append(parsedDate)

		meanVertices = []
		def getMeanVertexDegree(graph):
			meanVertices.append(np.mean(list(map(lambda x: x[1], graph.degree(weight='weight')))))

		medianVertices = []
		def getMedianVertexDegree(graph):
			medianVertices.append(np.median(list(map(lambda x: x[1], graph.degree(weight='weight')))))

		fracSizes = []
		secondFracSizes = []
		def getFractionalSizeOfTwoLargestComponents(graph):
			components = list(nx.connected_components(graph))
			maxComponent = max(components, key=len)
			fracSizes.append(len(maxComponent) / len(graph.nodes))
			components.remove(maxComponent)
			if components:
				secondMaxComponent = max(components, key=len)
				secondFracSizes.append(len(secondMaxComponent) / len(graph.nodes))
			else:
				secondFracSizes.append(0)

		meanShortestPaths = []
		def getMeanShortestPathLengthInLargestComponent(graph):
			largestComponent = max(nx.connected_component_subgraphs(graph), key=len)
			meanShortestPaths.append(nx.average_shortest_path_length(largestComponent, weight=None))

		clusteringCoefficients = []
		def getClusteringCoefficient(graph):
			clusteringCoefficients.append(nx.average_clustering(graph))
		
		pickle_path = 'data/{}/{}-duncan-watts-values.pickle'.format(pickle_dir, dirname)
		previously_calculated_values = pickle.load(open(pickle_path, 'rb')) if os.path.isfile(pickle_path) else {}

		files_dir = os.path.join(root_files_dir, os.fsencode(dirname), os.fsencode('playersonly'))
		listdir_ = sorted(os.listdir(files_dir))
		for idx, file_name in enumerate(listdir_):
			file_path = os.path.join(files_dir, file_name)
			if os.path.isfile(file_path) and os.fsdecode(file_name).endswith('.graphml'):
				try:
					g = nx.read_graphml(file_path).to_undirected()
					if len(g.nodes) > 0: # graph is not empty
						if 'windowDates' not in previously_calculated_values.keys():
							getDate(file_name)
						if 'meanVertices' not in previously_calculated_values.keys():
							getMeanVertexDegree(g)
						if 'medianVertices' not in previously_calculated_values.keys():
							getMedianVertexDegree(g)
						if 'fracSizes' not in previously_calculated_values.keys() or 'secondFracSizes' not in previously_calculated_values.keys():
							getFractionalSizeOfTwoLargestComponents(g)
						if 'meanShortestPaths' not in previously_calculated_values.keys():
							getMeanShortestPathLengthInLargestComponent(g)
						if 'clusteringCoefficients' not in previously_calculated_values.keys():
							getClusteringCoefficient(g)
				except:
					print('Problem with file {}'.format(os.fsdecode(file_name)))
				else:
					print('Processed {} out of {} files in {}'.format(idx + 1, len(listdir_) - 1, dirname))
				finally:
					g = None

		if 'windowDates' not in previously_calculated_values.keys():
			previously_calculated_values['windowDates'] = windowDates
		if 'meanVertices' not in previously_calculated_values.keys():
			previously_calculated_values['meanVertices'] = meanVertices
		if 'medianVertices' not in previously_calculated_values.keys():
			previously_calculated_values['medianVertices'] = medianVertices
		if 'fracSizes' not in previously_calculated_values.keys():
			previously_calculated_values['fracSizes'] = fracSizes
		if 'secondFracSizes' not in previously_calculated_values.keys():
			previously_calculated_values['secondFracSizes'] = secondFracSizes
		if 'meanShortestPaths' not in previously_calculated_values.keys():
			previously_calculated_values['meanShortestPaths'] = meanShortestPaths
		if 'clusteringCoefficients' not in previously_calculated_values.keys():
			previously_calculated_values['clusteringCoefficients'] = clusteringCoefficients

		with open('data/{}/{}-duncan-watts-values-updated.pickle'.format(pickle_dir, dirname), 'wb') as file:
			pickle.dump(previously_calculated_values, file, protocol=pickle.HIGHEST_PROTOCOL)

		plotAllPlots(previously_calculated_values, plots, getLineStyle(dirname))
	plt.savefig('imagenes/{}/test-duncan-watts-metrics.pdf'.format(pickle_dir))


def plotAllPlots(previously_calculated_values, plots, line_style):
	(meanVerticesPlot, fracSizesPlot, meanShortestPathsPlot, clusteringCoefficientsPlot) = plots
	windowDates = previously_calculated_values['windowDates']
	meanVertices = previously_calculated_values['meanVertices']
	medianVertices = previously_calculated_values['medianVertices']
	fracSizes = previously_calculated_values['fracSizes']
	secondFracSizes = previously_calculated_values['secondFracSizes']
	meanShortestPaths = previously_calculated_values['meanShortestPaths']
	clusteringCoefficients = previously_calculated_values['clusteringCoefficients']

	meanVerticesPlot.plot_date(windowDates, meanVertices, linestyle=line_style, marker=None, linewidth=0.5)
	# meanVerticesPlot.plot_date(windowDates, medianVertices, linestyle=line_style, marker=None, linewidth=0.5)
	fracSizesPlot.plot_date(windowDates, fracSizes, linestyle=line_style, marker=None, linewidth=0.5)
	# fracSizesPlot.plot_date(windowDates, secondFracSizes, linestyle=line_style, marker=None, linewidth=0.5)
	meanShortestPathsPlot.plot_date(windowDates, meanShortestPaths, linestyle=line_style, marker=None, linewidth=0.5)
	clusteringCoefficientsPlot.plot_date(windowDates, clusteringCoefficients, linestyle=line_style, marker=None, linewidth=0.5)



if __name__ == '__main__':
	main()
