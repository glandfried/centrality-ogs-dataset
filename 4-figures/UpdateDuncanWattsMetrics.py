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
	fig, plots = plt.subplots(4, sharex=True)
	for dirname in ['oneweek', 'overlapping', 'onemonth']:
		previously_calculated_values = pickle.load(open('../3-results/{}-duncan-watts-values-updated.pickle'.format(dirname), 'rb'))
		plotAllPlots(previously_calculated_values, plots, getLineStyle(dirname))
	plt.savefig('pdf/duncan-watts-metrics.pdf')
	return

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
