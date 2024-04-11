import math
import pickle
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from scipy import stats
import os
import seaborn as sns

CENTRALITY_NAMES = [#'information-centrality',
                    'degree-centrality',
                    'load-centrality',
                    'eigenvector-centrality',
                    'closeness-centrality-inverse-distance',
                    'betweenness-centrality',
                    #'current-flow-betweenness-centrality',
                    'communicability-betweenness-centrality',
                    'harmonic-centrality-inverse-weight']


def main():
    game_order_folder = 'enddate'
    centrality_per_player = pickle.load(open('../3-results/centrality-per-player.pickle'.format(game_order_folder), 'rb'))
    skill_windows_pp = pickle.load(
        open('../3-results/ttt-experience-evolution-windows-per-player.pickle'.format(game_order_folder), 'rb'))

    skill_evolution = {}
    ttt_level = None
    if '--ttt-inicial-low' in sys.argv:
        ttt_level = "low"
        #player_skill = [ (player, skills) for player, skills in skill_windows_pp.items()]
        for player, skills in skill_windows_pp.items():#player, skills =player_skill[0]
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 7 <= flattened[0][0] <= 10:
                skill_evolution[player] = flattened
    elif '--ttt-inicial-med' in sys.argv:
        ttt_level = "med"
        for player, skills in skill_windows_pp.items():
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 13 <= flattened[0][0] <= 14:
                skill_evolution[player] = flattened
    elif '--ttt-inicial-high' in sys.argv:
        ttt_level = "high"
        for player, skills in skill_windows_pp.items():
            flattened = [skill_std_pair for window in skills for skill_std_pair in window]
            if len(flattened) > 0 and 16 <= flattened[0][0] <= 18:
                skill_evolution[player] = flattened

    games_number = 150

    active_players = set()
    skill_values = []
    for player, skills in skill_evolution.items():
        if len(skills) >= games_number:
            active_players.add(player)
            skill_values.append(skills)

    print('Number of active players: {}'.format(len(active_players)))

    def get_number_of_windows_until_50_games(player_windows):
        user_games = 0
        for window_idx, window in enumerate(player_windows):
            user_games += len(window)
            if user_games >= 50:
                return window_idx + 1
        raise Exception('Player must have played at least 50 games')

    def get_summarized_centrality(centrality_values, number_of_windows):
        if '--mean' in sys.argv:
            return np.mean(centrality_values[:number_of_windows])  # Solo las primeras 50 partidas
        return np.median(centrality_values[:number_of_windows])  # Solo las primeras 50 partidas

    sns.set(rc={
        "axes.axisbelow": False,
        "axes.edgecolor": "dimgrey",
        "axes.facecolor": "None",
        "axes.grid": False,
        "axes.labelcolor": "dimgrey",
        "axes.spines.right": False,
        "axes.spines.top": False,
        "figure.facecolor": "white",
        "lines.solid_capstyle": "round",
        "patch.force_edgecolor": False,
        "text.color": "dimgrey",
        "xtick.bottom": True,
        "xtick.color": "dimgrey",
        "xtick.direction": "out",
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "axes.labelsize": 16,
        "xtick.top": False,
        "ytick.color": "dimgrey",
        "ytick.direction": "out",
        "ytick.left": True,
        "ytick.right": False
    })
    
    #centrality_groups = pickle.load(open('data/enddate/centrality-categorization-value-groups.pickle', 'rb'))
    centrality_groups = pickle.load(open('../3-results/150-games-centrality-categorization-value-groups.pickle', 'rb'))
    for centrality in CENTRALITY_NAMES:#centrality="degree-centrality"
        low_outliers, low_percentile, med_percentile, high_percentile, high_outliers, = centrality_groups[centrality]
        print("LOW: {}, MID: {}, HIGH: {}".format(low_percentile, med_percentile, high_percentile))

        low_centrality_players = set()
        medium_centrality_players = set()
        high_centrality_players = set()

        for player in active_players:#player=list(active_players)[0]
            windows_until_50_games = get_number_of_windows_until_50_games(skill_windows_pp[player])
            values = centrality_per_player[centrality][player]
            centrality_value = get_summarized_centrality(values, windows_until_50_games)
            if low_outliers < centrality_value <= low_percentile:
                low_centrality_players.add(player)
            elif low_percentile < centrality_value <= med_percentile:
                medium_centrality_players.add(player)
            elif med_percentile < centrality_value <= high_outliers:
                high_centrality_players.add(player)

        def get_summary():
            if '--mean' in sys.argv:
                return 'mean'
            return 'median'

        print("Players with low cent: {}".format(len(low_centrality_players)))
        print("Players with medium cent: {}".format(len(medium_centrality_players)))
        print("Players with high cent: {}".format(len(high_centrality_players)))

        if '--pickle-only' in sys.argv:
            continue

        fig, exp_skill_ax = plt.subplots()
        exp_skill_ax.set_xlim([1, games_number])
        exp_skill_ax.get_yaxis().set_major_formatter(ticker.FormatStrFormatter("%.2f"))
        exp_skill_ax.get_yaxis().set_minor_formatter(ticker.FormatStrFormatter("%.2f"))
        exp_skill_ax.set_ylabel('Skill ({})'.format(get_axis_name()))
        exp_skill_ax.set_xlabel('Experience (games played)')

        min_skill = 100
        max_skill = 0
        for cent_band, player_set in [('low', low_centrality_players),('high', high_centrality_players)]:#('medium', medium_centrality_players),
            #cent_band, player_set = ('low', low_centrality_players)
            n = len(player_set )
            mean = []
            stde = []
            game_numbers = []
            for game in range(1, games_number + 1):#game=1
                mu_values = []; sigma2_values = []
                for player in player_set:#player=3859
                    player_skills = skill_evolution[player]
                    if len(player_skills) > game:
                        skill_value, uncert_value = player_skills[game - 1]
                        #if not math.isnan(skill_value):
                        mu_values.append(skill_value/n)
                        sigma2_values.append((uncert_value/n)**2)
                if mu_values:
                    mean.append(np.sum(mu_values))
                    stde.append(np.sqrt(np.sum(sigma2_values)))
                    game_numbers.append(game)

            mean = np.array(mean)
            stde = np.array(stde)
            if '--ttt-inicial-high' in sys.argv:
                max_skill = 17.70
                min_skill = 15.45
            if '--ttt-inicial-med' in sys.argv:
                max_skill = 14.8
                min_skill = 12.9
            if '--ttt-inicial-low' in sys.argv:
                max_skill = 11.50
                min_skill = 8.5


            overall_mean_skill = np.mean(mean)
            print("Centrality: {}, centrality band: {}, Overall mean skill: {}".format(centrality, cent_band,overall_mean_skill))

            exp_skill_ax.plot(game_numbers, mean, label="{} centrality ({} ind.)".format(cent_band, len(player_set)))
            exp_skill_ax.fill_between(game_numbers, mean - 2*stde, mean + 2*stde, alpha=0.2)

        exp_skill_ax.set_ylim([min_skill, max_skill])
        exp_skill_ax.legend(loc='lower right', fontsize='large')
        #fig.suptitle(get_fig_title(centrality, len(active_players)), fontsize=13)
        fig.savefig("pdf/evolucion-{}-{}.pdf".format(get_file_name(),centrality),bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        nombre = "pdf/evolucion-{}-{}.pdf".format(get_file_name(),centrality)
        os.system("pdfcrop -m '0 0 0 0' {} {}".format(nombre,nombre))


def get_file_name():
    if '--ttt-inicial-med' in sys.argv:
        return 'ttt-inicial-med'
    elif '--ttt-inicial-low' in sys.argv:
        return 'ttt-inicial-low'
    elif '--ttt-inicial-high' in sys.argv:
        return 'ttt-inicial-high'


def get_fig_title(centrality, players):
    title = centrality.replace('-', ' ').title()
    return title


def get_axis_name():
    return 'TrueSkill Through Time'


if __name__ == '__main__':
    main()
