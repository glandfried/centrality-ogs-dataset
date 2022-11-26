all: duncanWatts initialTTTHistogram centralities learningCurves

duncanWatts: ../3-results/results.zip
	python3 UpdateDuncanWattsMetrics.py

initialTTTHistogram: ../3-results/results.zip
	python3 InitialTTTHistogram.py

centralities: ../3-results/results.zip
	python3 CentralityCategorizationInitialTTT.py

learningCurves: ../3-results/results.zip
	python3 CentralityCategorizationInitialTTT.py --ttt-inicial-low
	python3 CentralityCategorizationInitialTTT.py --ttt-inicial-med
	python3 CentralityCategorizationInitialTTT.py --ttt-inicial-high

../3-results/results.zip:
	make -C ../3-results/
