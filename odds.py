import math
import random
import tkinter as tk

# CONFIG ITEMS
# higher weights means more numbers, less likely to lose
NAMES = ['Ex1', 'Ex2']
WEIGHTS = [10, 10]
LOSS_DESCRIPTION = 'loses!'

# UNCHANGEABLE CONFIG
_draft_y_position = 500
_game_x_position = 100

_draft_box_width = 100
_draft_box_height = 20
_game_box_width = 20
_game_box_height = 60

_flash_time_multiplier = 1

_max_baits = 10
_speed_pps = 180
_refresh_rate_ps = 60

_bait_max_pct = .8
_bait_degrade_ratio = 1.5  # the
_bait_min_max_pct = (35, 85)  # percentage out of 100, must be whole number


class LateNightCanvas(tk.Canvas):
    def __init__(self, root):
        super().__init__(root, width=900, height=600)

        self.master.title('Late Night')
        self.pack()

    # --------- Draft Helpers ---------
    def make_person_draft_rectangle(self, x_position, health, name=None):
        y_offset = (health * 20) - 20
        y = _draft_y_position - y_offset
        self.create_rectangle(x_position, y, x_position + 100, y - 20, outline="#013220", fill="green")
        if name:
            # first time
            self.create_text(x_position + 50, _draft_y_position + 10, anchor=tk.N, font=('Arial', 30, ''), text=name)
        return self.create_text(x_position + 50, _draft_y_position + 40, anchor=tk.N, font=('Arial', 30, ''),
                                text=str(health))

    # --------- Game Helpers ---------
    def make_person_game_health_label(self, y_position, health, name):
        return self.create_text(_game_x_position, y_position, anchor=tk.W, font=('Arial', 30, ''),
                                text=name + ': ' + str(health))

    def make_person_game_health_bar_name(self, y_position, health):
        health_bars = []
        for i in range(health):
            x_offset = i * 20
            x = _game_x_position + x_offset
            health_bar = self.create_rectangle(x, y_position + 20, x + 20, y_position + 80, outline="#013220",
                                               fill="green")
            health_bars.append(health_bar)
        return health_bars

    def remove_health_bar(self, health_bars):
        to_delete = health_bars.pop()
        self.delete(to_delete)

    # --------- Other Helpers ---------
    def move_symbol(self, start, end, symbol, color, anchor=tk.N):
        start_x, start_y = start
        end_x, end_y = end
        text = self.create_text(start_x, start_y, anchor=anchor, font=('Arial', 75, ''), fill=color, text=str(symbol))
        distance_to_travel = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        distance_per_second = distance_to_travel / _speed_pps
        num_frames = int(distance_per_second * _refresh_rate_ps)
        x_scale = (end_x - start_x) / num_frames
        y_scale = (end_y - start_y) / num_frames
        for _ in range(num_frames):
            self.move(text, x_scale, y_scale)
            self.update()
            self.after(int(1000 / _refresh_rate_ps))
        self.delete(text)

    @staticmethod
    def chose_player_and_path(start, all_players_top_of_stack, rounds, draft_array):
        num_players = len(all_players_top_of_stack)
        round_pct = rounds / (num_players * 5)
        cutoff = min(_bait_max_pct, round_pct)
        path = []
        redirects = 0
        last_person_chosen = None

        while redirects <= _max_baits:
            # chose a person to send the icon to
            person_chosen = random.choice(draft_array)
            if person_chosen == last_person_chosen:
                # do loop logic
                cutoff /= _bait_degrade_ratio
                redirects += 1
                continue

            # decide if it as bait or not
            rand = random.random()
            if rand > cutoff or redirects == _max_baits:  # not a bait
                # if it is not a bait, send it all the way
                path.append((start, all_players_top_of_stack[person_chosen]))
                return path, person_chosen

            # if it is a bait, send it _send_pct_on_bait, then run loop again
            send_pct_on_bait = random.randint(*_bait_min_max_pct)
            send_dcml_on_bait = send_pct_on_bait / 100
            fake_end_x, fake_end_y = all_players_top_of_stack[person_chosen]
            fake_midpoint_x = start[0] + ((fake_end_x - start[0]) * send_dcml_on_bait)
            fake_midpoint_y = start[1] + ((fake_end_y - start[1]) * send_dcml_on_bait)
            fake_midpoint = (fake_midpoint_x, fake_midpoint_y)
            path.append((start, fake_midpoint))

            # do loop logic
            cutoff /= _bait_degrade_ratio
            start = fake_midpoint
            last_person_chosen = person_chosen
            redirects += 1

        raise Exception('Critical game malfunction')  # this should never happen

    def move_symbol_with_fakeouts(self, start, all_players_top_of_stack, symbol, color, anchor, rounds, draft_array):
        paths, person_chosen = self.chose_player_and_path(start, all_players_top_of_stack, rounds, draft_array)
        for path in paths:
            start, end = path
            self.move_symbol(start, end, symbol, color, anchor)
        if person_chosen is None:
            raise Exception('Critical game error')
        return person_chosen

    def flash(self, txt, time):
        text = self.create_text(450, 250, anchor=tk.N, font=('Arial', 30, ''), text=txt)
        self.update()
        self.after(int(time * 1000 * _flash_time_multiplier))
        self.delete(text)


def get_list_of_non_player(player, num_players):
    players = list(range(num_players))
    players.remove(player)
    return players


def do_draft(canvas, num_players, num_numbers):
    person_x = [100, 700]  # two players
    if num_players == 3:
        person_x = [100, 400, 700]
    elif num_players == 4:
        person_x = [100, 300, 500, 700]
    elif num_players > 4:
        raise Exception('Max 4 players')

    heli = tk.PhotoImage(file="heli.gif")
    canvas.create_image(450, 5, anchor=tk.N, image=heli)

    # create a rectangle for each person
    person_y_top_of_stack_offsets = [60] * num_players
    person_healths = [1] * num_players
    person_health_texts = [canvas.make_person_draft_rectangle(person_x[x], 1, NAMES[x]) for x in range(num_players)]

    draft_array = []
    for i, weight in enumerate(WEIGHTS):
        draft_array += ([i] * weight)

    for i in range(num_numbers):
        drops_left = num_numbers - i
        if drops_left == 1:
            canvas.flash("1 health drop left", 1)
        elif drops_left % 2 == 0:
            canvas.flash(f"{str(drops_left)} health drops left", .5)

        all_players_top_of_stack = list(zip([x + 50 for x in person_x],
                                            [_draft_y_position - y for y in person_y_top_of_stack_offsets]))
        person_chosen = canvas.move_symbol_with_fakeouts((450, 90), all_players_top_of_stack, '+', 'green', tk.N, i,
                                                         draft_array)

        person_y_top_of_stack_offsets[person_chosen] += 20

        person_healths[person_chosen] += 1
        canvas.delete(person_health_texts[person_chosen])

        person_health_texts[person_chosen] = \
            canvas.make_person_draft_rectangle(person_x[person_chosen], person_healths[person_chosen])

    return person_healths


def do_game(canvas, num_players, person_healths):
    person_y = [150, 450]  # two players
    if num_players == 3:
        person_y = [150, 300, 450]
    elif num_players == 4:
        person_y = [50, 200, 350, 500]
    elif num_players > 4:
        raise Exception('Max 4 players')
    person_x_top_of_stack_offsets = [20 * health for health in person_healths]

    plane = tk.PhotoImage(file="plane.gif")
    canvas.create_image(600, 200, anchor=tk.W, image=plane)
    person_health_bars = [canvas.make_person_game_health_bar_name(person_y[x], person_healths[x])
                          for x in range(num_players)]

    person_health_texts = [canvas.make_person_game_health_label(person_y[x], person_healths[x], NAMES[x])
                           for x in range(num_players)]

    i = 0
    while 0 not in person_healths:
        choosing_options = []
        for person_index, person_health in enumerate(person_healths):
            choosing_options += [person_index] * person_health

        all_players_top_of_stack = list(zip([_game_x_position + x for x in person_x_top_of_stack_offsets],
                                            [y + 50 for y in person_y]))
        person_chosen = canvas.move_symbol_with_fakeouts((700, 300), all_players_top_of_stack, '-', 'red', tk.W, i,
                                                         choosing_options)

        person_x_top_of_stack_offsets[person_chosen] -= 20

        person_healths[person_chosen] -= 1

        # remove the health bar
        canvas.delete(person_health_bars[person_chosen].pop())

        # change the visual number
        canvas.delete(person_health_texts[person_chosen])
        person_health_texts[person_chosen] = canvas.make_person_game_health_label(person_y[person_chosen],
                                                                                  person_healths[person_chosen],
                                                                                  NAMES[person_chosen])
        i += 1

    return NAMES[person_healths.index(0)]


def main():
    if len(NAMES) != len(WEIGHTS):
        raise Exception('Weights must equal the length of the names')

    root = tk.Tk()
    num_players = len(NAMES)
    num_numbers = num_players * 5

    canvas = LateNightCanvas(root)

    # Initial setup
    canvas.flash(f"First to lose all their health {LOSS_DESCRIPTION}. Good luck!", 2)
    canvas.flash("Health kits dropping now...", 2)

    # -------- DRAFTING --------
    person_healths = do_draft(canvas, num_players, num_numbers)

    # Transition to playing
    canvas.update()
    canvas.after(2000)
    canvas.delete("all")
    canvas.flash("Health drops finished.", 2)
    canvas.flash("Enemy plane inbound! Watch out!", 2)

    # ------------ PLAYING GAME ------------
    name_of_loser = do_game(canvas, num_players, person_healths)

    # End the game
    canvas.update()
    canvas.after(1000)
    canvas.delete("all")

    # pop up loser name
    canvas.create_text(450, 150, anchor=tk.N, font=('Comic Sans MS', 150, ''), fill='red', text=name_of_loser)
    canvas.update()
    canvas.after(1000)
    # supporting text
    canvas.create_text(450, 400, anchor=tk.N, font=('Arial', 45, ''), text=LOSS_DESCRIPTION)
    canvas.update()
    canvas.after(9000)
    exit()

    tk.mainloop()


if __name__ == '__main__':
    main()
