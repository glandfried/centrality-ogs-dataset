#!/bin/bash

PATH_TO_EXPORTS=$'./data'
OVERLAPPED=$'overlapping'
OVERLAPPED_PATH=${PATH_TO_EXPORTS}/${OVERLAPPED}
ALL=$'all-batched'
ALL_PATH=${PATH_TO_EXPORTS}/${ALL}

command=$1

if [[ ${command} == 'dw' ]]; then
	python3 UpdateDuncanWattsMetrics.py "${OVERLAPPED_PATH}"/playersonly
	python3 DegreeDistribution.py "${ALL_PATH}"/playersonly
	python3 Fig4DW.py
elif [[ ${command} == 'graph-size' ]]; then
	python3 PlotGraphSizeEvolution.py "${ALL_PATH}"/playersonly
elif [[ ${command} == 'algorithms' ]]; then
	python3 Algorithms.py "${ALL_PATH}"/playersonly
elif [[ ${command} == 'exp-vs-glicko' ]]; then
	python3 ExperienceVsGlicko.py "${ALL_PATH}"
elif [[ ${command} == 'exp-vs-trueskill' ]]; then
	python3 ExperienceVsSkill.py "${ALL_PATH}"/trueskill --trueskill --enddate
elif [[ ${command} == 'exp-vs-ttt' ]]; then
	python3 ExperienceVsSkill.py "${ALL_PATH}" --ttt --enddate
elif [[ ${command} == 'centralities' ]]; then
	python3 Centralities.py "${ALL_PATH}"/playersonly --enddate
	python3 CentralityCategorizationInitialTTT.py
elif [[ ${command} == 'windows-per-player' ]]; then
	python3 WindowsPerPlayer.py
fi
