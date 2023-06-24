import random
from collections import Counter
import datetime
import sqlite3
from tabulate import tabulate


def computerFirstMove_Player1() -> str:
	"""
    function that returns random starting move for first computer player
    :return: str- the best random starting move
    """

	safe_moves = ('top-L', 'top-R', 'low-L', 'low-R')
	return random.choice(safe_moves)


def computerFirstMove_Player2(board: dict) -> str:
	"""
    function that returns starting move for second computer player
    :param board: dict-board dictionary
    :return: str- the best starting move / random alternative move
    """
	if board['mid-M'] == 0:
		return 'mid-M'
	# else
	safe_moves = ('top-L', 'top-R', 'low-L', 'low-R')
	return random.choice(safe_moves)


def printBoard(board: dict) -> None:
	"""
    function that prints current board
    :param board: dict- board dictionary
    :return: None
    """
	counter = 1
	for i in ('top', 'mid', 'low'):
		for j in ('L', 'M', 'R'):
			value = board[f'{i}-{j}']
			if value == 0:
				char = '\033[1;32m' + str(counter) + '\033[1;m'
			elif value == 1:
				char = '\033[1;35m' + 'X' + '\033[1;m'
			else:  # value == 2
				char = '\033[1;31m' + 'O' + '\033[1;m'
			print(f'[{char}]', end=' ')
			counter += 1
		print('\n')


def playerInput(board: dict) -> str:
	"""
    function that gets user input and validates it
    :param board: dict- board dictionary
    :return: str- board key user insertet
    """

	while True:
		i = input("Enter board position: ")
		if i.isdigit():
			i = int(i)
			if 1 <= i <= 9:
				if board[numToKey(i - 1)] == 0:
					break
				else:
					print('This point is occupied!')
			else:
				print('Enter right range!')
		else:
			print('Enter integers!')
	return numToKey(i - 1)


def numToKey(num: int) -> str:
	"""
    function to convert user input to dictionary key
    :param num: int- user input
    :return: str- key value
    """

	keyDict = {0: 'top-L', 1: 'top-M', 2: 'top-R', 3: 'mid-L', 4: 'mid-M', 5: 'mid-R', 6: 'low-L', 7: 'low-M',
			   8: 'low-R'}
	return keyDict[num]


def evaluateBoard(board: dict, player: int, wantedCount: int, emptySize: int) -> tuple:
	"""
	function to evaluate board: finds win/loss/draw situations
	function also used to find the best computer move
    :param board: board
	:param player: player number
	:param wantedCount: how many player mark are needed for win/loss. use =2 for computer move, =3 for evaluation
	:param emptySize: how many empty squares are required for win/loss. use =1 for computer move, =0 for evaluation
	:return: tuple- [0]: best move if there is (str) None if not / evaluation mode. [1]: evaluation status (str)
    """

	if player == 1:
		other = 2
	else:
		other = 1

	rows = ('top', 'mid', 'low')
	columns = ('L', 'M', 'R')

	# forks list
	dangerous = []

	# service lambdas
	ret = lambda lst, string: (lst[0], string) if emptySize != 0 else (None, string)  # check for evaluation mode return
	val = lambda: f'{i}-{j}' if check == 0 else f'{j}-{i}'  # check if rows or columns are checked

	# check rows and columns
	for check in range(2):
		for i in rows:
			empty = []
			p1Count = 0
			p2Count = 0
			for j in columns:
				value = board[val()]
				if value == player:
					p1Count += 1
				elif value == other:
					p2Count += 1
				else:
					empty.append(val())

			# win
			if p1Count == wantedCount and len(empty) == emptySize:
				return ret(empty, 'win')
			# threat
			if p2Count == wantedCount and len(empty) == emptySize:
				return ret(empty, 'loss')

			# check for forks
			if len(empty) == 2 and p2Count == 1:
				dangerous.append(empty)

		rows, columns = columns, rows  # swap rows and columns to check another dimension

	# check diagonals
	diagonal = ('top-L', 'mid-M', 'low-R')
	for check in range(2):
		empty = []
		p1Count = 0
		p2Count = 0
		for i in diagonal:
			value = board[i]
			if value == player:
				p1Count += 1
			elif value == other:
				p2Count += 1
			else:
				empty.append(i)

			# win
			if p1Count == wantedCount and len(empty) == emptySize:
				return ret(empty, 'win')
			# threat
			if p2Count == wantedCount and len(empty) == emptySize:
				return ret(empty, 'loss')

		# check for forks
		# if len(empty) == 2 and p2Count == 1:
		# dangerous.append(empty)

		# change to secondary diagonal
		diagonal = ('top-R', 'mid-M', 'low-L')

	# find common points between forks
	if len(dangerous) > 0:
		# get all forks intercepts
		counts = Counter([x for sublist in dangerous for x in sublist])
		common_values = [val for val, count in counts.items() if count == 2]
		# if one point, block it
		if len(common_values) == 1:
			return common_values[0], 'defended fork'
		# more than one point, choose a random point that defends from the fork
		elif len(common_values) >= 2:
			# if possible, always prefer corners
			tp = None
			if any([board[x] == 0 for x in ('top-L', 'top-R', 'low-L', 'low-R')]):
				tp = ('top-L', 'top-R', 'low-L', 'low-R')
			while True:
				temp = random.choice(random.choice(dangerous))
				if board[temp] == 0 and temp not in common_values:
					if tp is None:
						return temp, 'defended fork'
					# if corner or no corner available return
					elif temp in tp or all(
							[board[x] != 0 or x in common_values for x in ('top-L', 'top-R', 'low-L', 'low-R')]):
						return temp, 'defended fork'

	# return draw if there is no move
	if all(board.values()) != 0:
		return None, 'draw'

	# if no forks, play random
	while True:
		tp = ('top-L', 'top-M', 'top-R', 'mid-L', 'mid-M', 'mid-R', 'low-L', 'low-M', 'low-R')
		temp = random.choice(tp)
		if board[temp] == 0:
			return temp, 'random'


def computerMove(board: dict, player: int, first: bool) -> tuple:
	"""
	function that chooses the computer move whenever it's the first move or not
	:param board: dict - board dictionary
	:param player: int - player number
	:param first: bool - is first move or not
	:return: tuple - [0]: chosen move. [1]: set first to False
	"""

	# first move protocol
	if first:
		if any(board.values()) != 0:
			move = computerFirstMove_Player2(board)
			return move, False
		else:
			move = computerFirstMove_Player1()
			return move, False

	# get a move
	move = evaluateBoard(board, player, 2, 1)[0]

	return move, False


def PvP(board: dict) -> tuple:
	"""
    game function of player versus player mode
    :param board: dict- board dictionary
    :return: tuple- [0]: 1 if player 1 wins, 2 if player 2 wins, 0 if draw. [1]: player who started
    """

	turn = random.randint(1, 2)
	started = turn

	while True:
		printBoard(board)
		stat = evaluateBoard(board, 1, 3, 0)[1]
		if stat == 'win':
			print('Player 1 won!')
			return 1, started
		elif stat == 'loss':
			print('Player 2 won!')
			return 2, started
		elif stat == 'draw':
			print('draw!')
			return 0, started

		if turn == 1:
			print('Player 1 turn!')
			move = playerInput(board)
			board[move] = 1
			turn = 2
			continue
		if turn == 2:
			print('Player 2 turn!')
			move = playerInput(board)
			board[move] = 2
			turn = 1


def PvC(board: dict) -> tuple:
	"""
    game function of player versus computer mode
    :param board: dict- board dictionary
    :return: tuple- [0]: 1 if player 1 wins, 2 if player 2 wins, 0 if draw. [1]: player who started
    """

	turn = random.randint(1, 2)
	started = turn
	first = True

	while True:
		printBoard(board)
		stat = evaluateBoard(board, 1, 3, 0)[1]
		if stat == 'win':
			print('Player 1 won!')
			return 1, started
		elif stat == 'loss':
			print('Computer won!')
			return 2, started
		elif stat == 'draw':
			print('draw!')
			return 0, started

		if turn == 1:
			print('Player 1 turn!')
			move = playerInput(board)
			board[move] = 1
			turn = 2
			continue
		if turn == 2:
			print('Computer turn!')
			move, first = computerMove(board, turn, first)
			board[move] = 2
			turn = 1


def CvC(board: dict) -> tuple:
	"""
    game function of computer versus computer mode
    :param board: dict- board dictionary
    :return: tuple- [0]: 1 if player 1 wins, 2 if player 2 wins, 0 if draw. [1]: player who started
    """

	turn = random.randint(1, 2)
	started = turn
	first1 = True
	first2 = True

	while True:
		stat = evaluateBoard(board, 1, 3, 0)[1]
		if stat == 'win':
			printBoard(board)
			print('Computer 1 won!')
			return 1, started
		elif stat == 'loss':
			printBoard(board)
			print('Computer 2 won!')
			return 2, started
		elif stat == 'draw':
			printBoard(board)
			print('draw!')
			return 0, started

		if turn == 1:
			move, first1 = computerMove(board, turn, first1)
			if move is None:
				printBoard(board)
				print('draw!')
				return 0, started
			board[move] = 1
			turn = 2
			continue
		if turn == 2:
			move, first2 = computerMove(board, turn, first2)
			if move is None:
				printBoard(board)
				print('draw!')
				return 0, started
			board[move] = 2
			turn = 1


def main() -> None:
	"""
	main function. has the interface and game functions
	:return: None
	"""

	# create sqlite database
	connection = sqlite3.connect(":memory:")
	cursor = connection.cursor()
	# create new table
	cursor.execute(""" CREATE TABLE IF NOT EXISTS dataBase (
	            date TEXT,
	            p1 TEXT,
	            p2 TEXT,
	            started TEXT,
	            winner TEXT
	            ); """)
	# menu
	while True:
		board = {'top-L': 0, 'top-M': 0, 'top-R': 0,
				 'mid-L': 0, 'mid-M': 0, 'mid-R': 0,
				 'low-L': 0, 'low-M': 0, 'low-R': 0}

		print('\nwelcome to Tic-Tac-Toe! Choose one option:\n1. Player vs. Player\n2. Player vs. Computer\n3. Computer '
			  'vs. Computer\n4. Game History\n5. Quit\n')

		inp = input('Type your choice: ')
		print()

		if inp == '1':
			p1 = input('Enter P1 name: ')
			p2 = input('Enter P2 name: ')
			result, started = PvP(board)
			# update database
			winner = {0: 'draw', 1: p1, 2: p2}
			cursor.execute("INSERT INTO dataBase VALUES (?,?,?,?,?)",
						   (str(datetime.datetime.now()), p1, p2, winner[started], winner[result]))
			connection.commit()

		elif inp == '2':
			p1 = input('Enter P1 name: ')
			p2 = 'Computer 2'
			result, started = PvC(board)
			# update database
			winner = {0: 'draw', 1: p1, 2: p2}
			cursor.execute("INSERT INTO dataBase VALUES (?,?,?,?,?)",
						   (str(datetime.datetime.now()), p1, p2, winner[started], winner[result]))
			connection.commit()

		elif inp == '3':
			p1 = 'Computer 1'
			p2 = 'Computer 2'
			result, started = CvC(board)
			# update database
			winner = {0: 'draw', 1: p1, 2: p2}
			cursor.execute("INSERT INTO dataBase VALUES (?,?,?,?,?)",
						   (str(datetime.datetime.now()), p1, p2, winner[started], winner[result]))
			connection.commit()

		elif inp == '4':
			while True:
				print(
					'\nGame History:\n1. type \'all\' to view full history\n2. type player name to view all their game '
					'history\n3. type \'back\' to go back to main options\n')

				inp = input('Type here: ')

				if inp == 'all':
					# display database
					cursor.execute("SELECT * FROM dataBase")  # Fetching data
					head = ['Date', 'X', 'O', 'started', 'Winner']
					print('\nAll history:\n')
					data = tabulate(cursor, headers=head, tablefmt="fancy_grid", numalign="center")
					print(data)
					continue

				if inp == 'back':
					break

				else:
					# search and display with filter
					data = (inp, inp)
					cursor.execute("SELECT * FROM dataBase WHERE p1 = ? OR p2 = ?", data)
					head = ['Date', 'X', 'O', 'started', 'Winner']
					data = tabulate(cursor, headers=head, tablefmt="fancy_grid", numalign="center")
					print(f'\nHistory featuring \'{inp}\':\n')
					print(data)

		elif inp == '5':
			connection.close()
			return


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(e)
	finally:
		quit()