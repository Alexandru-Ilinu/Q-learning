
from argparse import ArgumentParser
from random import randint, random, choice
from time import sleep
from copy import copy
import sys


WALL = '#'
EMPTY = ' '
PADDLE = '#'
BALL = "o"

REWARD_WIN = 1.0
REWARD_LOSE = -1.0

DIRECTIONS = ["LEFT_UP", "LEFT", "LEFT_DOWN", "RIGHT_UP", "RIGHT", "RIGHT_DOWN"]
ACTIONS = ["UP", "DOWN", "STAY"]
RANDOM, GREEDY, EPS_GREEDY = 0, 1, 2 			# strategia agentului
RANDOM_OPP, GREEDY_OPP, ALMOST_PERFECT_OPP = 0, 1, 2 	# strategia adversarului

# stare = (poz_agent, poz_adversar, poz_minge, directie_minge)
AGENT_POS = 0
OPPONENT_POS = 1
BALL_POS = 2
BALL_DIR = 3

MIN_VALUE = -1000


# intoarce starea initiala
def get_initial_state(args):
	half_r = args.table_height / 2 + 1

	# pozitia initiala a agentului este la mijlocul tablei
	pos = half_r

	# pozitia adversarului este tot la mijlocul tablei
	opp_pos = half_r

	# pozitia mingii (rand, coloana) - in centru
	row = half_r
	half_c = args.table_width / 2
	if args.table_width % 2 == 1:
		col = half_c + 1
	else:
		col = half_c

	rnd = randint(0, 5)
	direction = DIRECTIONS[rnd]

	return (pos, opp_pos, (row, col), direction)

# afiseaza o stare
def print_state(state, args):
	disp = Display(args.table_height + 2, args.table_width + 2)

	# afisez peretii orizontali
	for i in [0, args.table_height + 1]:
		for j in range(args.table_width + 2):
			disp.set_char(i, j, WALL)

	# afisez paletele
	for i in range(state[AGENT_POS] - args.paddle_size / 2, state[AGENT_POS] + args.paddle_size/2 + 1):
		disp.set_char(i, 0, PADDLE)
	for i in range(state[OPPONENT_POS] -  args.paddle_size / 2, state[OPPONENT_POS] + args.paddle_size/2 + 1):
		disp.set_char(i, args.table_width + 1, PADDLE)

	# afisez mingea
	(r, c) = state[BALL_POS]
	disp.set_char(r, c, BALL)

	disp.disp()

# verifica daca o stare este terminala
def is_terminal_state(state, args):
	(b_r, b_c) = state[BALL_POS]
	return b_c == 0 or b_c == args.table_width + 1

# returneaza lista cu actiunile posibile din starea curenta 
# pentru jucatorul player (AGENT_POS sau OPPONENT_POS)
def get_available_actions(state, player, args):
	upper_paddle_row = state[player] - args.paddle_size / 2
	bottom_paddle_row = state[player] + args.paddle_size / 2

	if upper_paddle_row == 1:
		return ["DOWN", "STAY"]
	if bottom_paddle_row == args.table_height:
		return ["UP", "STAY"]
	return ACTIONS


def choose_action_agent_random(state, Q, args):
	avail_actions = get_available_actions(state, AGENT_POS, args)
	return choice(avail_actions)

def choose_action_agent_greedy(state, Q, args):
	avail_actions = get_available_actions(state, AGENT_POS, args)
	max_q = MIN_VALUE
	for action in avail_actions:
		q = get_q(Q, (state, action))
		if q > max_q:
			max_q = q
			max_action = action
	return max_action

def get_unexplored_actions(state, Q):
	avail_actions = get_available_actions(state, AGENT_POS, args)
	explored_actions = [a for (s, a) in Q.keys() if s == state]
	return [action for action in ACTIONS if action not in explored_actions and action in avail_actions]

def choose_action_agent_eps_greedy(state, Q, args):
	unexplored_actions = get_unexplored_actions(state, Q)
	if unexplored_actions:
		return choice(unexplored_actions)
	else:
		rnd = random()
		if rnd < args.epsilon:
			return choose_action_agent_random(state, Q, args)
		else:
			return choose_action_agent_greedy(state, Q, args)

def choose_action_agent(state, Q, args):
	if args.agent_strategy == RANDOM:
		return choose_action_agent_random(state, Q, args)
	if args.agent_strategy == GREEDY:
		return choose_action_agent_greedy(state, Q, args)
	if args.agent_strategy == EPS_GREEDY:
		return choose_action_agent_eps_greedy(state, Q, args)

# executa actiunea pentru jucatorul player
def execute_action(state, action, player):
	new_state = list(state)
	if action == "UP":
		new_state[player] = new_state[player] - 1
	elif action == "DOWN":
		new_state[player] = new_state[player] + 1
	return tuple(new_state)


def choose_action_opponent_random(state, Q, args):
	avail_actions = get_available_actions(state, OPPONENT_POS, args)
	return choice(avail_actions)

def mirror_direction(direction):
	ind = DIRECTIONS.index(direction)
	nr_dirs = len(DIRECTIONS)
	return DIRECTIONS[(ind + nr_dirs/2) % nr_dirs]

def make_mirror_state(state, args):
	pos = state[OPPONENT_POS]
	opponent_pos = state[AGENT_POS]
	(r, c) = state[BALL_POS]
	c2 = args.table_width + 1 - c
	direction = mirror_direction(state[BALL_DIR])
	return (pos, opponent_pos, (r, c2), dir)

def choose_action_opponent_greedy(state, Q, args):
	mirror_state = make_mirror_state(state, args)
	return choose_action_agent_greedy(mirror_state, Q, args)


def choose_action_opponent_almost_perfect(state, Q, args):
	if random() < args.alpha:
		return choose_action_opponent_random(state, Q, args)
	else:
		(ball_r, _) = state[BALL_POS]
		pos_r = state[OPPONENT_POS]
		avail_actions = get_available_actions(state, OPPONENT_POS, args)
		if ball_r < pos_r:
			if "UP" in avail_actions:
				return "UP"
			else:
				return "STAY"
		elif ball_r > pos_r:
			if "DOWN" in avail_actions:
				return "DOWN"
			else:
				return "STAY"
		else:
			return "STAY"

def choose_action_opponent(state, Q, args):
	if args.opponent_strategy == RANDOM_OPP:
		return choose_action_opponent_random(state, Q, args)
	if args.opponent_strategy == GREEDY_OPP:
		return choose_action_opponent_greedy(state, Q, args)
	if args.opponent_strategy == ALMOST_PERFECT_OPP:
		return choose_action_opponent_almost_perfect(state, Q, args)

def get_opponents_move(state, Q, args):
	action = choose_action_opponent(state, Q, args)
	new_state = execute_action(state, action, OPPONENT_POS)
	return new_state

def get_q(Q, k):
	if k not in Q:
		return 0
	return Q[k]

def update_Q(Q, state, action, reward, new_state):

	old_q = get_q(Q, (state, action))
	avail_actions = get_available_actions(new_state, AGENT_POS, args)

	max_q = MIN_VALUE
	for future_action in avail_actions:
		q = get_q(Q, (new_state, future_action))
		if q > max_q:
			max_q = q

	Q[(state, action)] = old_q + args.learning_rate * (reward + args.discount * max_q - old_q)


def get_next_ball_pos(state, args):
	(r, c) = state[BALL_POS]
	return get_next_ball_pos_from_dir((r, c), state[BALL_DIR])

def get_next_ball_pos_from_dir(pos, dir):
	(r, c) = pos
	if dir == "LEFT_UP":
		r -= 1
		c -= 1
	if dir == "LEFT":
		c -= 1
	if dir == "LEFT_DOWN":
		r += 1
		c -= 1
	if dir == "RIGHT_UP":
		r -= 1
		c += 1
	if dir == "RIGHT":
		c += 1
	if dir == "RIGHT_DOWN":
		r += 1
		c += 1
	return (r, c)

	
def move_along_dir(state):
	return get_next_ball_pos_from_dir(state[BAL_POS], state[BALL_DIR])

def is_paddle_at(state, player, row, args):
	if row >= state[player] - args.paddle_size/2 and row <= state[player] + args.paddle_size/2:
		return True
	else:
		return False

def rebound_dir(state, player):
	r1 = state[player]
	(r2, _) = state[BALL_POS]
	if r1 == r2:
		return "HORIZONTAL"
	elif r1 < r2:
		return "DOWN"
	else:
		return "UP"

def is_left(dir):
	return DIRECTIONS.index(dir) < 3

def is_right(dir):
	return not is_left(dir)

def find_rebound_dir(state, rebound_dir):
	current_dir = state[BALL_DIR]
	if rebound_dir == "HORIZONTAL":
		if is_left(current_dir):
			return "RIGHT"
		else:
			return "LEFT"
	elif rebound_dir == "DOWN":
		if is_left(current_dir):
			return "RIGHT_DOWN"
		else:
			return "LEFT_DOWN"
	elif rebound_dir == "UP":
		if is_left(current_dir):
			return "RIGHT_UP"
		else:
			return "LEFT_UP"

def ball_dir_after_hitting_paddle(state, player, args):
	reb_dir = rebound_dir(state, player)
	return find_rebound_dir(state, reb_dir)


def get_next_ball_dir(state, args):
	(r, c) = state[BALL_POS]
	
	if state[BALL_DIR] == "LEFT":
		if c == 1:
			if is_paddle_at(state, AGENT_POS, r, args):
				return ball_dir_after_hitting_paddle(state, AGENT_POS, args)

	elif state[BALL_DIR] == "RIGHT":
		if c == args.table_width:
			if is_paddle_at(state, OPPONENT_POS, r, args):
				return ball_dir_after_hitting_paddle(state, OPPONENT_POS, args)

	elif state[BALL_DIR] == "LEFT_UP":
		if c == 1 and r == 1:
			if is_paddle_at(state, AGENT_POS, 2, args):
				return "RIGHT_DOWN"
			else:
				return "LEFT_DOWN"
		elif c == 1:
			if is_paddle_at(state, AGENT_POS, r - 1, args):
				return ball_dir_after_hitting_paddle(state, AGENT_POS, args)
		elif r == 1:
			return "LEFT_DOWN"

	elif state[BALL_DIR] == "LEFT_DOWN":
		if r == args.table_height and c == 1:
			if is_paddle_at(state, AGENT_POS, args.table_height - 1, args):
				return "RIGHT_UP"
			else:
				return "LEFT_UP"
		elif r == args.table_height:
			return "LEFT_UP"
		elif c == 1:
			if is_paddle_at(state, AGENT_POS, r + 1, args):
				return ball_dir_after_hitting_paddle(state, AGENT_POS, args)

	elif state[BALL_DIR] == "RIGHT_UP":
		if r == 1 and c == args.table_width:
			if is_paddle_at(state, OPPONENT_POS, 2, args):
				return "LEFT_DOWN"
			else:
				return "RIGHT_DOWN"
		elif r == 1:
			return "RIGHT_DOWN"
		elif c == args.table_width:
			if is_paddle_at(state, OPPONENT_POS, r - 1, args):
				return ball_dir_after_hitting_paddle(state, OPPONENT_POS, args)

	elif state[BALL_DIR] == "RIGHT_DOWN":
		if r == args.table_height and c == args.table_width:
			if is_paddle_at(state, OPPONENT_POS, args.table_height - 1, args):
				return "LEFT_UP"
			else:
				return "RIGHT_UP"
		elif r == args.table_height:
			return "RIGHT_UP"
		elif c == args.table_width:
			if is_paddle_at(state, OPPONENT_POS, r + 1, args):
				return ball_dir_after_hitting_paddle(state, OPPONENT_POS, args)

	return state[BALL_DIR]


def move_ball(state, args):
	new_state = list(state)
	new_state[BALL_DIR] = get_next_ball_dir(state, args)
	new_state[BALL_POS] = get_next_ball_pos(new_state, args)
	return tuple(new_state)


def get_reward(state, args):
	(_, ball_c) = state[BALL_POS]
	if ball_c == 0:
		return REWARD_LOSE
	if ball_c == args.table_width + 1:
		return REWARD_WIN
	return 0


class Display:

	def __init__(self, nrows, ncols):
		self.nrows = nrows
		self.ncols = ncols
		self.chars = []
		for i in range(self.nrows):
			self.chars.append(self.ncols * [EMPTY])

	def disp(self):
		for i in range(self.nrows):
			print "".join(self.chars[i])
		print

	def set_char(self, i, j, c):
		self.chars[i][j] = c

	def get_char(self, i, j):
		return self.chars[i][j]

def print_parameters(args):
	print "Learning rate: " + str(args.learning_rate)
	print "Discount: " + str(args.discount)
	print "Epsilon: " + str(args.epsilon)
	print "Alpha: " + str(args.alpha)
	print "Agent's strategy: " + str(args.agent_strategy)
	print "Opponent's strategy: " + str(args.opponent_strategy)

def print_parameters_training(args, i, nr_frames, nr_won, nr_lost):
	print "Etapa: antrenare"
	print "Episod: " + str(i + 1) + "/" + str(args.train_episodes)
	print "Frame: " + str(nr_frames) + "/" + str(args.max_frames)
	print_parameters(args)
	print "Scor: AGENT - " + str(nr_won) + "; ADVERSAR - " + str(nr_lost)

def print_parameters_eval(args, i, nr_frames, nr_won, nr_lost):
	print "Etapa: testare"
	print "Episod: " + str(i + 1) + "/" + str(args.eval_episodes)
	print "Frame: " + str(nr_frames) + "/" + str(args.max_frames)
	print_parameters(args)
	print "Scor: AGENT - " + str(nr_won) + "; ADVERSAR - " + str(nr_lost)


if __name__ == "__main__":
	

	parser = ArgumentParser()
	parser.add_argument("--table_width", type = int, default = 5, help = "Width of the table (without the paddle column)")
	parser.add_argument("--table_height", type = int, default = 5, help = "Height of the table (without the vertical walls)")
	parser.add_argument("--paddle_size", type = int, default = 3, help = "Size of the paddle")

	parser.add_argument("--learning_rate", type = float, default = 0.1, help = "Learning rate")
	parser.add_argument("--discount", type = float, default = 0.99, help = "Value for the discount factor")
	parser.add_argument("--epsilon", type = float, default = 0.05, help = "Probability to choose a random action.")
	parser.add_argument("--alpha", type = float, default = 0.1, help = "Probability with which the almost-perfect opponent selects a random action.")

	parser.add_argument("--train_episodes", type = int, default = 10, help = "Number of episodes")
	parser.add_argument("--eval_episodes", type = int, default = 10, help = "Number of games to play for evaluation.")
	parser.add_argument("--max_frames", type = int, default = 30, help = "Maximum number of frames per episode")
	parser.add_argument("--sleep", type = float, default = 0.1, help = "Seconds to 'sleep' between moves.")

	parser.add_argument("--agent_strategy", type = int, default = RANDOM, help = "Agent's strategy")
	parser.add_argument("--opponent_strategy", type = int, default = RANDOM_OPP, help = "Opponent's strategy")
	parser.add_argument("--sleep2", type = float, default = 0.1, help = "Sleep time between two episodes. ")

	args = parser.parse_args()
	
	
	Q = {}

	# etapa de antrenare
	nr_won = 0
	nr_lost = 0
	nr_ties = 0
	for i in range(args.train_episodes):

		state = get_initial_state(args)
		nr_frames = 0

		while not is_terminal_state(state, args):

			nr_frames = nr_frames + 1
			if nr_frames > args.max_frames:
				#print "Egalitate. "
				sleep(args.sleep2)
				nr_ties += 1
				break

			print_parameters_training(args, i, nr_frames, nr_won, nr_lost)

			# agentul selecteaza actiunea
			action = choose_action_agent(state, Q, args)

			# agentul executa actiunea
			next_state = execute_action(state, action, AGENT_POS)
			print_state(next_state, args)
			sleep(args.sleep)

			print_parameters_training(args, i, nr_frames, nr_won, nr_lost)

			# mingea avanseaza
			next_state = move_ball(next_state, args)
			print_state(next_state, args)
			sleep(args.sleep)

			reward = get_reward(next_state, args)

			# daca mingea nu a trecut de adversar
			if reward != REWARD_WIN:

				print_parameters_training(args, i, nr_frames, nr_won, nr_lost)

				# adversarul alege miscarea si o executa
				next_state = get_opponents_move(next_state, Q, args)
				print_state(next_state, args)
				sleep(args.sleep)

			# actualizez valorile din Q
			update_Q(Q, state, action, reward, next_state)

			# daca am castigat
			if reward == REWARD_WIN:
				#print "Agentul a CASTIGAT jocul. "
				sleep(args.sleep2)
				nr_won += 1
				break
			# daca am pierdut
			elif reward == REWARD_LOSE:
				#print "Agentul a pierdut jocul. "
				sleep(args.sleep2)
				nr_lost += 1
				break

			state = next_state


	# etapa de testare
	args.sleep = 0.04 ####

	nr_won = 0
	nr_lost = 0
	nr_ties = 0
	for i in range(args.eval_episodes):

		state = get_initial_state(args)
		nr_frames = 0

		while not is_terminal_state(state, args):

			nr_frames = nr_frames + 1
			if nr_frames > args.max_frames:
				nr_ties += 1
				#print "Egalitate. "
				break

			print_parameters_eval(args, i, nr_frames, nr_won, nr_lost)

			action = choose_action_agent(state, Q, args)
			#print "Actiune agent: " + action
			next_state = execute_action(state, action, AGENT_POS)
			print_state(next_state, args)
			sleep(args.sleep)

			next_state = move_ball(next_state, args)

			print_parameters_eval(args, i, nr_frames, nr_won, nr_lost)

			print_state(next_state, args)
			sleep(args.sleep)

			reward = get_reward(next_state, args)

			if reward == REWARD_WIN:
				#print "Agentul a castigat jocul. "
				nr_won += 1
				break

			elif reward == REWARD_LOSE:
				#print "Agentul a pierdut jocul. "
				nr_lost += 1
				break
			if reward != REWARD_WIN:

				print_parameters_eval(args, i, nr_frames, nr_won, nr_lost)

				next_state = get_opponents_move(next_state, Q, args)
				print_state(next_state, args)
				sleep(args.sleep)

			state = next_state


