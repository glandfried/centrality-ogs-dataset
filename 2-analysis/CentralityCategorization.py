import math
import pickle
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from scipy import stats

CENTRALITY_NAMES = [#'information-centrality',
                    'degree-centrality',
                    'load-centrality',
                    'eigenvector-centrality',
                    'closeness-centrality-inverse-distance',
                    'betweenness-centrality',
                    #'current-flow-betweenness-centrality',
                    'communicability-betweenness-centrality',
                    'harmonic-centrality-inverse-weight']


# Toma las centralidades calculadas para cada jugador en Centralities.py, y las categoriza en tres grupos: low, medium y high.
# Cada uno de estos grupos se refiere al valor de centralidad que tuvo el jugador, tomando algun criterio para resumir la informacion, dado que cada jugador tiene asociada una lista con sus correspondientes valores de centralidad a lo largo del tiempo.
# Por ejemplo, se puede resumir la evolucion de la centralidad para el jugador X como la media de sus centralidades, o el maximo, o como el promedio. Una vez se tiene un unico numero para cada jugador, se lo ubica en el grupo correspondiente (utilizando percentiles).
#
# Este script genera un pickle para cada algoritmo de centralidad, conteniendo un diccionario con keys [low, medium,
# high], y los jugadores correspondientes en cada grupo.
# Tambien genera un grafico de (valor de centralidad vs. habilidad) para cada centralidad, dibujando las curvas para
# cada una de los 3 grupos de centralidad.
def main():
    if '--startdate' not in sys.argv and '--enddate' not in sys.argv:
        raise Exception('Must pass either --enddate or --startdate params to choose game order folder')
    game_order_folder = 'startdate' if '--startdate' in sys.argv else 'enddate'

    centrality_per_player = pickle.load(open('data/{}/centrality-per-player.pickle'.format(game_order_folder), 'rb'))

    skill_evolution = {}
    if '--trueskill' in sys.argv:
        skill_evolution = pickle.load(
            open('data/{}/trueskill-experience-evolution-per-player-and-board.pickle'.format(game_order_folder), 'rb'))
    elif '--ttt' in sys.argv:
        skill_windows_pp = pickle.load(
            open('data/{}/ttt-experience-evolution-windows-per-player.pickle'.format(game_order_folder), 'rb'))
        for player, skills in skill_windows_pp.items():
            skill_evolution[player] = [skill_std_pair for window in skills for skill_std_pair in window]
    elif '--ttt-inicial' in sys.argv:
        skill_windows_pp = pickle.load(
            open('data/{}/ttt-experience-evolution-windows-per-player.pickle'.format(game_order_folder), 'rb'))
        for player, skills in skill_windows_pp.items():
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 38 <= flattened[0][0] <= 41:
                skill_evolution[player] = flattened
    elif '--ttt-inicial-low' in sys.argv:
        skill_windows_pp = pickle.load(
            open('data/{}/ttt-experience-evolution-windows-per-player.pickle'.format(game_order_folder), 'rb'))
        for player, skills in skill_windows_pp.items():
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 25 <= flattened[0][0] <= 37:
                skill_evolution[player] = flattened
    elif '--ttt-inicial-high' in sys.argv:
        skill_windows_pp = pickle.load(
            open('data/{}/ttt-experience-evolution-windows-per-player.pickle'.format(game_order_folder), 'rb'))
        for player, skills in skill_windows_pp.items():
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 42 <= flattened[0][0] <= 55:
                skill_evolution[player] = flattened
    else:
        skill_evolution = pickle.load(
            open('data/{}/glicko-experience-evolution-per-player-and-board.pickle'.format(game_order_folder), 'rb'))

    games_number = 250

    active_players = set()
    skill_values = []
    for player, skills in skill_evolution.items():
        if len(skills) >= games_number:
            active_players.add(player)
            skill_values.append(skills)

    print('Number of active players: {}'.format(len(active_players)))

    def getSummarizedCentrality(centrality_values):
        if '--ttt-inicial' in sys.argv or '--ttt-inicial-low' in sys.argv or '--ttt-inicial-high' in sys.argv:
            return np.nanmedian(centrality_values[:50])  # Solo las primeras 50 partidas
        if '--mean' in sys.argv:
            return np.nanmean(centrality_values)
        elif '--median' in sys.argv:
            return np.nanmedian(centrality_values)
        elif '--max' in sys.argv:
            return np.nanmax(centrality_values)
        else:  # default is last cent value
            return next(i for i in reversed(centrality_values) if not math.isnan(i))

    for centrality in CENTRALITY_NAMES:
        all_processed_cents = []
        for player in active_players:
            user_cent_values = centrality_per_player[centrality][player]
            processed_cent = getSummarizedCentrality(user_cent_values)
            all_processed_cents.append(processed_cent)

        low_percentile = np.percentile(all_processed_cents, 33)
        med_percentile = np.percentile(all_processed_cents, 67)

        low_centrality_players = set()
        medium_centrality_players = set()
        high_centrality_players = set()

        for player in active_players:
            values = centrality_per_player[centrality][player]
            centrality_value = getSummarizedCentrality(values)
            if centrality_value < low_percentile:
                low_centrality_players.add(player)
            elif low_percentile <= centrality_value < med_percentile:
                medium_centrality_players.add(player)
            elif med_percentile <= centrality_value:
                high_centrality_players.add(player)

        def get_summary():
            if '--mean' in sys.argv:
                return 'mean'
            elif '--median' in sys.argv:
                return 'median'
            elif '--max' in sys.argv:
                return 'max'
            else:
                return 'last'

        with open('data/{}/{}-{}-categorization-groups.pickle'.format(game_order_folder, get_summary(), centrality), 'wb') as handle:
            pickle.dump(
                {"low": low_centrality_players, "medium": medium_centrality_players, "high": high_centrality_players},
                handle, protocol=pickle.HIGHEST_PROTOCOL)

        print("Players with low cent: {}".format(len(low_centrality_players)))
        print("Players with medium cent: {}".format(len(medium_centrality_players)))
        print("Players with high cent: {}".format(len(high_centrality_players)))

        if '--pickle-only' in sys.argv:
            continue

        fig, exp_skill_ax = plt.subplots()
        exp_skill_ax.set_xlim([1, games_number])
        exp_skill_ax.get_yaxis().set_major_formatter(ticker.FormatStrFormatter("%.0f"))
        exp_skill_ax.get_yaxis().set_minor_formatter(ticker.FormatStrFormatter("%.0f"))
        exp_skill_ax.set_ylabel('Habilidad ({})'.format(get_axis_name()))
        exp_skill_ax.set_xlabel('Experiencia (partidas jugadas)')

        for cent_band, player_set in [('low', low_centrality_players), ('medium', medium_centrality_players),
                                      ('high', high_centrality_players)]:
            mean = []
            stde = []
            game_numbers = []
            for game in range(1, games_number + 1):
                values = []
                for player in player_set:
                    player_skills = skill_evolution[player]
                    if len(player_skills) > game:
                        skill_value, _ = player_skills[game - 1]
                        if not math.isnan(skill_value):
                            values.append(skill_value)
                if values:
                    mean.append(np.mean(values))
                    stde.append(stats.sem(values, nan_policy='omit'))
                    game_numbers.append(game)

            mean = np.array(mean)
            stde = np.array(stde)
            overall_mean_skill = np.mean(mean)
            if '--trueskill' in sys.argv or '--ttt' in sys.argv or '--ttt-inicial' in sys.argv or '--ttt-inicial-low' in sys.argv or '--ttt-inicial-high' in sys.argv:
                print("Centrality: {}, centrality band: {}, Overall mean skill: {}".format(centrality, cent_band,
                                                                                           overall_mean_skill))
                exp_skill_ax.plot(game_numbers, mean, label="{} centrality".format(cent_band))
                exp_skill_ax.fill_between(game_numbers, mean - stde, mean + stde, alpha=0.2)  # color='gray'
            else:
                # 1500 glicko is considered base Glicko: https://forums.online-go.com/t/ogs-has-a-new-glicko-2-based-rating-system/13058
                probability_of_winning = 1 / (1 + 10 ** (-(overall_mean_skill - 1500) / 400))
                print("Centrality: {}, centrality band: {}, Overall mean skill: {}, prob of winning: {}".format(
                    centrality, cent_band, overall_mean_skill, probability_of_winning))
                exp_skill_ax.plot(game_numbers, mean, label="{} centrality: {:.1f}% prob. of winning".format(cent_band,
                                                                                                             probability_of_winning * 100))
                exp_skill_ax.fill_between(game_numbers, mean - stde, mean + stde, alpha=0.2)  # color='gray'

        exp_skill_ax.legend(loc='lower right', fontsize='x-small')
        fig.savefig("imagenes/{}/evolucion-skill-centralities/evolucion-{}-{}.pdf".format(game_order_folder,
                                                                                          get_file_name(), centrality))
        plt.close(fig)


def get_file_name():
    if '--trueskill' in sys.argv:
        return 'trueskill'
    elif '--ttt' in sys.argv:
        return 'ttt'
    elif '--ttt-inicial' in sys.argv:
        return 'ttt-inicial'
    elif '--ttt-inicial-low' in sys.argv:
        return 'ttt-inicial-low'
    elif '--ttt-inicial-high' in sys.argv:
        return 'ttt-inicial-high'
    else:
        return 'glicko'


def get_axis_name():
    if '--trueskill' in sys.argv:
        return 'TrueSkill'
    elif '--ttt' in sys.argv or '--ttt-inicial' in sys.argv or '--ttt-inicial-low' in sys.argv or '--ttt-inicial-high' in sys.argv:
        return 'TrueSkill Through Time'
    else:
        return 'Glicko'


if __name__ == '__main__':
    main()
