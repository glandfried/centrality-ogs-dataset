# coding=utf-8

import os
import pickle
import sys
import math
import numpy
import csv
from datetime import datetime
from scipy import stats

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import networkx as nx


def plot_experience_vs_skill_mean_per_game(skill_evolution, game_order_folder, skilltype):
    skill_values = list(skill_evolution.values())
    games_number = 150
    skills_filtered = list(filter(lambda skill: len(skill) >= games_number, skill_values))
    mean = []
    variance = []
    population = []
    for game in range(games_number):
        values = []
        for player_skills in skills_filtered:
            if len(player_skills) > max(10, game):
                skill_value, _ = player_skills[game]
                if not math.isnan(skill_value):
                    values.append(skill_value)
        if values:
            mean.append(numpy.mean(values))
            variance.append(stats.sem(values, nan_policy='omit'))
            population.append(len(values))
        else:
            mean.append(0)
            variance.append(0)
            population.append(0)
    mean = numpy.array(mean)
    variance = numpy.array(variance)
    p = plt.plot(range(1, len(mean) + 1), mean)
    plt.fill_between(range(1, len(mean) + 1), mean - variance, mean + variance, color=p[-1].get_color(), alpha=0.2)

    plt.title(u'Población con {}+ partidas: {}'.format(games_number, population[0]))
    plt.yscale('log')
    # plt.gca().get_yaxis().set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    # plt.gca().get_yaxis().set_minor_formatter(ticker.FormatStrFormatter("%.0f"))
    # plt.tick_params(axis='y', which='minor')
    plt.xscale('log')
    # plt.yticks(numpy.arange(min(mean), max(variance)+100, 200))
    plt.ylabel('Habilidad ({})'.format(
        'TrueSkill' if skilltype == 'trueskill' else ('TTT' if skilltype == 'ttt' else 'Glicko')))
    plt.xlabel('Experiencia (partidas jugadas)')
    plt.savefig('imagenes/{}/hist-evolucion-{}.pdf'.format(game_order_folder, skilltype))
    plt.clf()

    ############################################################

    exponents = [3, 4, 5, 6, 7, 8, 9, 10]
    for exp_idx in range(len(exponents) - 1):
        games_number = 2 ** exponents[exp_idx]
        skills_filtered = list(
            filter(lambda glicko: 2 ** exponents[exp_idx] <= len(glicko) < 2 ** exponents[exp_idx + 1], skill_values))

        mean = []
        variance = []
        population = []
        for game in range(games_number):
            values = []
            for player_skills in skills_filtered:
                if len(player_skills) > game:
                    skill_value, _ = player_skills[game]
                    if not math.isnan(skill_value):
                        values.append(skill_value)
            if values:
                mean.append(numpy.mean(values))
                variance.append(stats.sem(values, nan_policy='omit'))
                population.append(len(values))
            else:
                mean.append(0)
                variance.append(0)
                population.append(0)

        mean = numpy.array(mean)
        variance = numpy.array(variance)
        plt.plot(range(1, len(mean) + 1), mean,
                 label='Entre {} y {} partidas jugadas'.format(2 ** exponents[exp_idx], 2 ** exponents[exp_idx + 1]))
        plt.fill_between(range(1, len(mean) + 1), mean - variance, mean + variance, color='gray', alpha=0.2)
    # plt.ylim([1400,1700])
    # plt.xlim([0,500])
    plt.legend(loc='lower right', fontsize='x-small')
    plt.yscale('log')
    plt.xscale('log')
    # plt.yticks(numpy.arange(min(mean), max(variance)+100, 200))
    plt.ylabel('Habilidad ({})'.format(
        'TrueSkill' if skilltype == 'trueskill' else ('TTT' if skilltype == 'ttt' else 'Glicko')))
    plt.xlabel('Experiencia (partidas jugadas)')
    plt.gca().get_yaxis().set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    plt.gca().get_yaxis().set_minor_formatter(ticker.FormatStrFormatter("%.0f"))
    plt.savefig("imagenes/{}/hist-evolucion-{}-poblaciones.pdf".format(game_order_folder, skilltype))
    plt.clf()


# with open('data/glicko-evolution-population-{}.pickle'.format(board_sizes_names[idx]), 'wb') as handle:
# 	pickle.dump(population, handle, protocol=pickle.HIGHEST_PROTOCOL)

# plt.plot(population)
# plt.ylabel('Número de jugadores')
# plt.xlabel('Experiencia (partidas jugadas)')
# plt.yscale('log')
# plt.xscale('log')
# plt.savefig("imagenes/population-vs-experience-{}.pdf".format(board_sizes_names[idx]))
# plt.clf()


def main():
    if '--startdate' not in sys.argv and '--enddate' not in sys.argv:
        raise Exception('Must pass either --enddate or --startdate params to choose game order')
    game_order_folder = 'startdate' if '--startdate' in sys.argv else 'enddate'
    skilltype = 'trueskill' if '--trueskill' in sys.argv else ('ttt' if '--ttt' in sys.argv else 'glicko')
    if '--graph-only' in sys.argv:
        exp_evol_per_player = pickle.load(
            open('data/{}/{}-experience-evolution-per-player-and-board.pickle'.format(game_order_folder, skilltype),
                 'rb'))
        plot_experience_vs_skill_mean_per_game(exp_evol_per_player, game_order_folder, skilltype)
        return
    files_dir = os.fsencode(sys.argv[1])
    #files_dir = os.fsencode("./data/all-batched/")
    experience_evolution_per_player = {}
    experience_evolution_windows_per_player = {}
    mean_experience_evolution_per_player = {}
    all_sorted_games_per_player = {}
    ttt = {}
    ttt_filtered_games = set()
    if '--ttt' in sys.argv:
        with open('data/ttt_all_end.csv') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                ttt[int(row['id'])] = row
        with open('data/filtered_data.csv') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                ttt_filtered_games.add(int(row['id']))
    listdir_ = sorted(os.listdir(files_dir))
    for idx, file_name in enumerate(listdir_):#file_name=listdir_[140]
        file_path = os.path.join(files_dir, file_name)
        if os.path.isfile(file_path) and os.fsdecode(file_name).endswith(".graphml"):
            g = nx.read_graphml(file_path).to_undirected()
            print("Loaded batch {} of {}".format(idx + 1, len(listdir_) - 1))
            #playersNodes =  [node for node in g.nodes if g.nodes[node]['labels'] == ':Player']
            for playerNode in [node for node in g.nodes if g.nodes[node]['labels'] == ':Player']:#playerNode =playersNodes[30]
                def extract_skill_and_board_size(game_node):
                    if g.nodes[playerNode].get('ogsId'):
                        skill = 'unknown'
                        if '--trueskill' in sys.argv:
                            skill = game_node['whiteTrueSkill'] if game_node['whitePlayer'] == g.nodes[playerNode][
                                'ogsId'] else game_node['blackTrueSkill']
                        else:
                            skill = game_node['whiteGlicko'] if game_node['whitePlayer'] == g.nodes[playerNode][
                                'ogsId'] else game_node['blackGlicko']
                        return (float('NaN') if skill == 'unknown' else float(skill), game_node['size'])
                    else:
                        return (float('NaN'), game_node['size'])

                def extract_ttt_skill_and_std(game_node):
                    gameId = int(game_node['ogsId'])
                    if gameId in ttt_filtered_games:
                        return None
                    else:
                        return (float(ttt[gameId]['w_mean']), float(ttt[gameId]['w_std'])) \
                            if game_node['whitePlayer'] == g.nodes[playerNode]['ogsId'] \
                            else (float(ttt[gameId]['b_mean']), float(ttt[gameId]['b_std']))

                def getSortKey(game):
                    key = None
                    if '--enddate' in sys.argv:
                        key = 'endDate'
                    elif '--startdate' in sys.argv:
                        key = 'startDate'

                    try:
                        return datetime.strptime(game[key], "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError as _:
                        return datetime.strptime(game[key], "%Y-%m-%dT%H:%MZ")

                games_played_by_player = [g.nodes[game_id] for game_id in g[playerNode]]
                sorted_games = sorted(games_played_by_player, key=getSortKey)
                if not all_sorted_games_per_player.get(g.nodes[playerNode]['ogsId']):
                    all_sorted_games_per_player[g.nodes[playerNode]['ogsId']] = []
                all_sorted_games_per_player[g.nodes[playerNode]['ogsId']].append(list(sorted_games))

                skill_board_size_pairs = list(
                    map(extract_ttt_skill_and_std if '--ttt' in sys.argv else extract_skill_and_board_size,sorted_games))
                if '--ttt' in sys.argv:
                    game_index = 0
                    while game_index < len(skill_board_size_pairs) and not skill_board_size_pairs[game_index]:#GL: Es siempre falso.
                        game_index += 1
                    skill_board_size_pairs = skill_board_size_pairs[game_index:]

                    for i in range(len(skill_board_size_pairs)):
                        if not skill_board_size_pairs[i]:#GL: Es siempre falso.
                            skill_board_size_pairs[i] = skill_board_size_pairs[i - 1]

                if not experience_evolution_windows_per_player.get(g.nodes[playerNode]['ogsId']):
                    experience_evolution_windows_per_player[g.nodes[playerNode]['ogsId']] = []
                if len(skill_board_size_pairs) > 0:
                    experience_evolution_windows_per_player.get(g.nodes[playerNode]['ogsId']).append(
                        skill_board_size_pairs)

                experience_evolution_per_player[g.nodes[playerNode]['ogsId']] = experience_evolution_per_player.get(
                    g.nodes[playerNode]['ogsId'], []) + skill_board_size_pairs

                if '--ttt' not in sys.argv:
                    only_skills = [x[0] for x in skill_board_size_pairs if not math.isnan(x[0])]
                    current_means = mean_experience_evolution_per_player.get(g.nodes[playerNode]['ogsId'], [])
                    current_means.append(numpy.mean(only_skills) if len(only_skills) > 0 else (
                        current_means[-1] if len(current_means) > 0 else 0))
                    mean_experience_evolution_per_player[g.nodes[playerNode]['ogsId']] = current_means

    print("Finished getting list of skill values")

    with open('data/{}/{}-sorted-games-per-player.pickle'.format(game_order_folder, skilltype),'wb') as handle:
        pickle.dump(all_sorted_games_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if '--only-sorted-games' in sys.argv:
        return

    with open('data/{}/{}-experience-evolution-windows-per-player.pickle'.format(game_order_folder, skilltype),
              'wb') as handle:
        pickle.dump(experience_evolution_windows_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('data/{}/{}-experience-evolution-per-player-and-board.pickle'.format(game_order_folder, skilltype),
              'wb') as handle:
        pickle.dump(experience_evolution_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if '--ttt' not in sys.argv:
        with open('data/{}/{}-mean-experience-evolution-per-window-per-player.pickle'.format(game_order_folder,
                                                                                             skilltype),
                  'wb') as handle:
            pickle.dump(mean_experience_evolution_per_player, handle, protocol=pickle.HIGHEST_PROTOCOL)

        plot_experience_vs_skill_mean_per_game(experience_evolution_per_player, game_order_folder, skilltype)


if __name__ == '__main__':
    main()
