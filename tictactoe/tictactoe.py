"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    sumX = 0
    sumO = 0
    for x in range(3):
        for y in range(3):
            if board[x][y] == 'X':
                sumX += 1
            elif board[x][y] == 'O':
                sumO += 1
    
    #compare sums
    if sumX == sumO:
        return X
    else:
        return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()

    for j in range(3):
        for i in range(3):
            if board[j][i] == EMPTY:
                moves.add((j,i))

    return moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    copyboard = board

    if board[action[0]][action[1]] != EMPTY:
        raise Exception

    copyboard = deepcopy(board)
    copyboard[action[0]][action[1]] = player(board)

    return copyboard



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for x in range(3):
        if board[0][x] == board[1][x] == board[2][x] != EMPTY:
            if board[0][x] == 'X':
                return X
            else:
                return O
    
    for y in range(3):
        if board[y][0] == board[y][1] == board[y][2] != EMPTY:
            if board[y][0] == 'X':
                return X
            else: 
                return O
    
    if (board[0][0] == board[1][1] == board[2][2] != EMPTY):
        if(board[0][0] == 'X'):
            return X
        else: 
            return O 
    
    elif(board[2][0] == board[1][1] == board[0][2] != EMPTY):
        if(board[2][0] == 'X'):
            return X
        else: 
            return O
        
    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == 'X' or winner(board) == 'O' or not actions(board):
        return True
    return False



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == 'X':
        return 1
    elif winner(board) == 'O':
        return -1
    else:
        return 0



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    if player(board) == X:
        best_value = -math.inf
        best_action = None
        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_value:
                best_value = value
                best_action = action
        return best_action
    else:
        best_value = math.inf
        best_action = None
        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_value:
                best_value = value
                best_action = action
        return best_action


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    best_action = None
    for action in actions(board):
        value = min_value(result(board, action))
        if value > v:
            v = value
            best_action = action
    return v


def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    best_action = None
    for action in actions(board):
        value = max_value(result(board, action))
        if value < v:
            v = value
            best_action = action
    return v