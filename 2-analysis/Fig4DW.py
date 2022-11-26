import matplotlib.pyplot as plt
import numpy as np
import pickle
import matplotlib.gridspec as gs
from scipy import stats
import os

fig = plt.figure(tight_layout=True)
spec = gs.GridSpec(3, 2)

path = 'data/enddate/glicko-slicing-overview/degree-dist-20060516-20060530.pickle'
degs = pickle.load(open(path, "rb"))
total = len(degs)
bins = np.arange(0, 80, 10)
# Probabilidad Y de tener grado X
p,x = np.histogram(degs, bins=bins)
prob = list(map(lambda freq: freq/total, p))
ax = fig.add_subplot(spec[0, 0])
ax.plot(x[:-1], prob, marker='o')
ax.set_xscale('log')
ax.set_yscale('log')


path = 'data/enddate/glicko-slicing-overview/degree-dist-20130122-20130205.pickle'
degs = pickle.load(open(path, "rb"))
total = len(degs)
bins = np.arange(0, 80, 10)
# Probabilidad Y de tener grado X
p,x = np.histogram(degs, bins=bins)
prob = list(map(lambda freq: freq/total, p))
ax = fig.add_subplot(spec[0, 1])
ax.plot(x[:-1], prob, marker='o')
ax.set_xscale('log')
ax.set_yscale('log')


ks_values = []
p_values = []
path = 'data/enddate/glicko-slicing-overview/degree-dist-20060516-20060530.pickle'
degs1 = pickle.load(open(path, "rb"))
files_dir = 'data/enddate/glicko-slicing-overview'
listdir_ = sorted(os.listdir(files_dir))
for file_name in listdir_:
	file_path = os.path.join(files_dir, file_name)
	if os.path.isfile(file_path) and os.fsdecode(file_name).endswith('.pickle'):
		degs2 = pickle.load(open(file_path, "rb"))
		ks_values.append(stats.ks_2samp(degs1, degs2)[0])
		p_values.append(stats.ks_2samp(degs1, degs2)[1])

ax = fig.add_subplot(spec[1, :])
ax.plot(ks_values)

ax = fig.add_subplot(spec[2, :])
ax.plot(p_values)


fig.align_labels()
plt.savefig("imagenes/enddate/fig4dw.pdf")