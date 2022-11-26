import pickle
import sys

CENTRALITY_NAMES = ['information-centrality',
                    'degree-centrality',
                    'load-centrality',
                    'eigenvector-centrality',
                    'closeness-centrality-inverse-distance',
                    'betweenness-centrality',
                    'current-flow-betweenness-centrality',
                    'communicability-betweenness-centrality',
                    'harmonic-centrality-inverse-weight']

skilltype = 'ttt' if '--ttt' in sys.argv else 'trueskill'
windows_per_player = pickle.load(open('data/enddate/{}-experience-evolution-windows-per-player.pickle'.format(skilltype), 'rb'))
centralities = pickle.load(open('data/enddate/centrality-per-player.pickle', 'rb'))
unique_players_per_player = pickle.load(open('data/enddate/unique-players-per-player-per-window.pickle', 'rb'))

if len(centralities[CENTRALITY_NAMES[0]]) != len(windows_per_player.keys()):
    raise ValueError('Number of users does not match between the two pickles')

full_window_data = {}
for player, windows in windows_per_player.items():
    full_window_data[player] = []
    for index, window in enumerate(windows):
        window_data_for_player = {}
        for centrality in CENTRALITY_NAMES:
            window_data_for_player[centrality] = centralities[centrality][player][index]
        window_data_for_player['number-of-games'] = len(window)
        window_data_for_player['unique-players'] = unique_players_per_player[player][index]
        if index == 0:
            window_data_for_player['initial-skill'] = window[0][0]
            window_data_for_player['initial-std'] = window[0][1]
        else:
            window_data_for_player['initial-skill'] = windows[index-1][-1][0]
            window_data_for_player['initial-std'] = windows[index-1][-1][1]
        window_data_for_player['final-skill'] = window[-1][0]
        window_data_for_player['final-std'] = window[-1][1]
        full_window_data[player].append(window_data_for_player)

with open('data/{}-window-data-per-player.pickle'.format(skilltype), 'wb') as handle:
    pickle.dump(full_window_data, handle, protocol=pickle.HIGHEST_PROTOCOL)