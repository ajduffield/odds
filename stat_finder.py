import random

NUM_RUNS = 10000

names = ['a', 'b', 'c', 'd']
healths = [25, 25, 10, 40]


def find_loser():
    stat_list = []
    for name, health in zip(names, healths):
        stat_list += [name] * health
    while True:
        pick = random.randrange(len(stat_list))
        stat_list.pop(pick)
        # print(pick)
        # print(stat_list)
        for name in names:
            if name not in stat_list:
                return name

def main():
    losses = {name: 0 for name in names}
    for _ in range(NUM_RUNS):
        loser = find_loser()
        losses[loser] += 1
    print(losses)
    for name in names:
        # num_wins = NUM_RUNS - losses[name]
        print(f'{name} lose pct = {round(losses[name] / NUM_RUNS, 2)}')


if __name__ == '__main__':
    main()
