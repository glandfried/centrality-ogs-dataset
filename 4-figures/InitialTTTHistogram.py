import os
import pickle
import sys

import matplotlib.pyplot as plt
import seaborn as sns

CB91_Blue = '#2CBDFE'
CB91_Grey = '#D4D4D4'
CB91_Green = '#47DBCD'
CB91_Pink = '#F3A0F2'
CB91_Purple = '#9D2EC5'
CB91_Violet = '#661D98'
CB91_Amber = '#F5B14C'
CB91_Red = '#BC6566'
CB91_Brown = '#C2774F'


def played_at_least_x_games(windows, number_of_games):
    return number_of_games <= len([skill_std_pair for window in windows for skill_std_pair in window])


def main():
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
        "xtick.bottom": False,
        "xtick.color": "dimgrey",
        "xtick.direction": "out",
        "xtick.top": False,
        "ytick.color": "dimgrey",
        "ytick.direction": "out",
        "ytick.left": False,
        "ytick.right": False,
        'legend.fontsize': 'x-small'
    })

    skill_windows_pp = pickle.load(open('../3-results/ttt-experience-evolution-windows-per-player.pickle', 'rb'))
    min_number_of_games = next(
        (int(min_games.split("=")[1]) for min_games in sys.argv if min_games.startswith("--min-games=")), 150)
    game_values = [windows[0][0][0] for windows in skill_windows_pp.values() if
                   played_at_least_x_games(windows, min_number_of_games)]
    _, _, patches = plt.hist(game_values, bins=range(6, 21, 1), facecolor=CB91_Grey, rwidth=0.9)
    plt.xticks([7.5, 9.5,  13.5, 17])
    plt.xlabel('Initial skill (TTT)',fontsize=14)
    plt.ylabel('Number of players',fontsize=14)

    plt.annotate('Beginner', xy=(8.5, 173), xytext=(8.5, 175), xycoords='data', fontsize=14, ha='center',
                 va='bottom', color=CB91_Red,
                 arrowprops=dict(arrowstyle='-[, widthB=2, lengthB=0.7', lw=2.0, color=CB91_Red))
    for patch in patches[1:4]:
        patch.set_fc(CB91_Red)
    plt.gca().get_xticklabels()[0].set_color(CB91_Red)
    plt.gca().get_xticklabels()[1].set_color(CB91_Red)
    plt.annotate('Intermediate', xy=(13.5, 173), xytext=(13.5, 175), xycoords='data', fontsize=14, ha='center',
                 va='bottom', color=CB91_Amber,
                 arrowprops=dict(arrowstyle='-[, widthB=0.5, lengthB=0.7', lw=2.0, color=CB91_Amber))
    for patch in patches[7:8]:
        patch.set_fc(CB91_Amber)
    plt.gca().get_xticklabels()[2].set_color(CB91_Amber)
    plt.annotate('Expert', xy=(17, 173), xytext=(17, 175), xycoords='data', fontsize=14, ha='center',
                 va='bottom', color=CB91_Pink,
                 arrowprops=dict(arrowstyle='-[, widthB=1.5, lengthB=0.7', lw=2.0, color=CB91_Pink))
    for patch in patches[10:12]:
        patch.set_fc(CB91_Pink)
    plt.gca().get_xticklabels()[3].set_color(CB91_Pink)
    

    dir_name = 'pdf'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    plt.savefig(dir_name + '/hist-ttt-inicial-min-{}-partidas.pdf'.format(min_number_of_games), bbox_inches="tight", pad_inches=0)
    plt.clf()


if __name__ == "__main__":
    main()
