import os
import pickle
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import seaborn as sns
import networkx as nx
import numpy as np

CENTRALITIES = [#lambda x: nx.information_centrality(x, weight='weight', solver='lu'),
                nx.degree_centrality,
                lambda x: nx.load_centrality(x, weight='1/weight',normalized=True),#https://stackoverflow.com/questions/50497186/networkx-meaning-of-weight-in-betwenness-and-current-flow-betweenness
                lambda x: nx.eigenvector_centrality(x, max_iter=500000, weight='weight'),
                lambda x: nx.closeness_centrality(x, distance='1/weight', wf_improved=True),
                lambda x: nx.betweenness_centrality(x, weight='1/weight',normalized=True),#https://stackoverflow.com/questions/50497186/networkx-meaning-of-weight-in-betwenness-and-current-flow-betweenness
                #lambda x: nx.current_flow_betweenness_centrality(x, weight='weight', normalized=True, solver='full'),
                nx.communicability_betweenness_centrality,
                lambda x: nx.harmonic_centrality(x, distance='1/weight')]



CENTRALITY_NAMES = [#'information-centrality',
                    'degree-centrality',
                    'load-centrality',
                    'eigenvector-centrality',
                    'closeness-centrality-inverse-distance',
                    'betweenness-centrality',
                    #'current-flow-betweenness-centrality',
                    'communicability-betweenness-centrality',
                    'harmonic-centrality-inverse-weight']


CB91_Blue = '#2CBDFE'
CB91_Green = '#47DBCD'
CB91_Pink = '#F3A0F2'
CB91_Purple = '#9D2EC5'
CB91_Violet = '#661D98'
CB91_Amber = '#F5B14C'
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']


def get_number_of_windows_until_50_games(player_windows, until=50):
    user_games = 0
    for window_idx, window in enumerate(player_windows):
        user_games += len(window)
        if user_games >= until:
            return True, window_idx + 1
    return False, None


def played_x_games(x, windows):
    return sum([len(window) for window in windows]) >= x

def played_not_x_games(x, windows):
    return sum([len(window) for window in windows]) < x


def plot_centralities_hist(centralities_dict, game_order_folder, activos=True):
    #centralities_dict=centrality_per_player
    windows_per_player = pickle.load(open('data/enddate/ttt-experience-evolution-windows-per-player.pickle', 'rb'))
    centrality_groups = {}
    for centrality in CENTRALITY_NAMES:#centrality='degree-centrality'
        cent_means = []
        #user_values = [ [user, user_cent_values] for user, user_cent_values in centralities_dict[centrality].items() ]
        for user, user_cent_values in centralities_dict[centrality].items(): #user, user_cent_values = user_values[0]
            if activos and played_x_games(150, windows_per_player[user]):
                #sum([len(window) for window in windows_per_player[user]])
                played_50_games, windows_until_50_games = get_number_of_windows_until_50_games(windows_per_player[user])
                if played_50_games:
                    median = np.median(user_cent_values[:windows_until_50_games])
                    if median > 0:
                        cent_means.append(median)
            if (not activos) and played_not_x_games(51, windows_per_player[user]) and played_x_games(10, windows_per_player[user]):
                median = np.median(user_cent_values)
                cent_means.append(median)
                
        bins = None
        if centrality == 'harmonic-centrality-inverse-weight':
            bins = np.arange(0, 420, 4)
        elif centrality == 'closeness-centrality-inverse-distance':
            bins = np.arange(0.1, 0.45, (0.45-0.1)/100)
        else:
            bins = np.arange(max(min(cent_means),0.00001), max(cent_means), (max(cent_means)-max(min(cent_means),0.00001))/100 )
        
        #print(min(cent_means), max(cent_means), centrality)
        centrality_groups[centrality] = [(np.percentile(cent_means, 2)),(np.percentile(cent_means, 40)), (np.percentile(cent_means, 60)),(np.percentile(cent_means, 98)), max(cent_means)]

        sns.set(rc={
            "axes.axisbelow": False,
            "axes.edgecolor": "lightgrey",
            "axes.facecolor": "None",
            "axes.grid": False,
            "axes.labelcolor": "dimgrey",
            "axes.spines.right": False,
            "axes.spines.top": False,
            "figure.facecolor": "white",
            "lines.solid_capstyle": "round",
            "patch.force_edgecolor": False,
            "text.color": "dimgrey",
            "xtick.bottom": False,
            "xtick.color": "dimgrey",
            "xtick.direction": "out",
            "xtick.top": False,
            "ytick.color": "dimgrey",
            "ytick.direction": "out",
            "ytick.left": False,
            "ytick.right": False
        })
        sns.set_context("talk")
        hist, np_bins = np.histogram(cent_means, bins=bins)
        transformed_bins = np_bins
        fig, ax = plt.subplots()
        if centrality not in ['closeness-centrality-inverse-distance', 'harmonic-centrality-inverse-weight']:
            transformed_bins = np.logspace(np.log10(np_bins[0]), np.log10(np_bins[-1]), len(np_bins))
            plt.xscale('log')
        N, bins, patches  = ax.hist(cent_means, bins=transformed_bins, color='gray')
        for i in range(len(bins)):
            if (bins[i] >= centrality_groups[centrality][0]) and (bins[i] <= centrality_groups[centrality][1]):
                patches[i].set_facecolor(colors[0])
        for i in range(len(bins)):
            if (bins[i] >= centrality_groups[centrality][2]) and (bins[i] <= centrality_groups[centrality][3]):
                patches[i].set_facecolor(colors[1])
        if activos:
            plt.savefig('imagenes/{}/centralities/{}-150-partidas-hist.pdf'.format(game_order_folder, centrality), bbox_inches="tight")
        else: 
            plt.savefig('imagenes/{}/centralities/{}-150-partidas-hist-noactivos.pdf'.format(game_order_folder, centrality), bbox_inches="tight")
        plt.clf()

    if activos:
        with open('data/enddate/150-games-centrality-categorization-value-groups.pickle', 'wb') as handle:
            pickle.dump(centrality_groups, handle, protocol=pickle.HIGHEST_PROTOCOL)

def update_centrality_per_player(centrality_values,centrality_per_player, g, centrality_name):
    existing_values = centrality_per_player.get(centrality_name, {})
    for node in centrality_values.keys():
        existing_values[g.nodes[node]['ogsId']] = existing_values.get(g.nodes[node]['ogsId'], []) + [ centrality_values[node]]
        centrality_per_player[centrality_name] = existing_values

def main():
    if '--startdate' not in sys.argv and '--enddate' not in sys.argv:
        raise Exception('Must pass either --enddate or --startdate params to choose game order folder')
    game_order_folder = 'startdate' if '--startdate' in sys.argv else 'enddate'
    if '--graph-only' in sys.argv:
        centrality_per_player = pickle.load(
            open('data/{}/centrality-per-player.pickle'.format(game_order_folder), 'rb'))
        if '--no-activos' in sys.argv:
            plot_centralities_hist(centrality_per_player, game_order_folder, activos=False)
        else:
            plot_centralities_hist(centrality_per_player, game_order_folder)
        return
    files_dir = os.fsencode(sys.argv[1])
    centrality_per_player = {}
    listdir_ = sorted(os.listdir(files_dir))
    #percentiles = {c:[] for c in CENTRALITY_NAMES}
    for dir_idx, file_name in enumerate(listdir_):
        file_path = os.path.join(files_dir, file_name)
        if os.path.isfile(file_path) and os.fsdecode(file_name).endswith(".graphml"):
            print("Loaded batch {} of {}".format(dir_idx + 1, len(listdir_) - 1))
            graph = nx.read_graphml(file_path).to_undirected()
            for g in [graph.subgraph(c) for c in nx.algorithms.components.connected_components(graph)]:
                for u, v, d in g.edges(data=True):
                    d['1/weight'] = 1 / d['weight']

            for centrality_idx in range(len(CENTRALITIES)): #centrality_idx=0
                if CENTRALITY_NAMES[centrality_idx] in ['degree-centrality', 'eigenvector-centrality', 'closeness-centrality-inverse-distance', 'harmonic-centrality-inverse-weight','betweenness-centrality','load-centrality']:
                    centrality_values = CENTRALITIES[centrality_idx](graph)
                    update_centrality_per_player(centrality_values,centrality_per_player, graph, CENTRALITY_NAMES[centrality_idx])
                    #all_values = list(centrality_values.values())
                    #percentiles[CENTRALITY_NAMES[centrality_idx]].append([min(all_values), np.percentile(all_values, q=25), np.percentile(all_values, q=50), np.percentile(all_values, q=75), max(all_values) ] )

                if CENTRALITY_NAMES[centrality_idx] in ['information-centrality','communicability-betweenness-centrality','current-flow-betweenness-centrality']:#g=gs[1]
                    for g in [graph.subgraph(c) for c in nx.algorithms.components.connected_components(graph)]:
                        centrality_values = CENTRALITIES[centrality_idx](g)
                        update_centrality_per_player(centrality_values,centrality_per_player, g, CENTRALITY_NAMES[centrality_idx])
                        #all_values = list(centrality_values.values())
                        #percentiles[CENTRALITY_NAMES[centrality_idx]].append([min(all_values), np.percentile(all_values, q=25), np.percentile(all_values, q=50), np.percentile(all_values, q=75), max(all_values) ] )

    print("Finished getting centralities")
    with open('data/{}/centrality-per-player.pickle'.format(game_order_folder), 'wb') as handle:
        pickle.dump(centrality_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

    plot_centralities_hist(centrality_per_player, game_order_folder)


if __name__ == '__main__':
    main()
