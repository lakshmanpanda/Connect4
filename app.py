from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import math
import random

app = Flask(__name__)
CORS(app)

# Game constants
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

class Connect4Game:
    def __init__(self):
        self.board = np.zeros((ROW_COUNT, COLUMN_COUNT))
        self.game_over = False
        self.turn = random.randint(PLAYER, AI)

    def create_board(self):
        return np.zeros((ROW_COUNT, COLUMN_COUNT))

    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece

    def is_valid_location(self, board, col):
        return board[ROW_COUNT - 1][col] == 0

    def get_next_open_row(self, board, col):
        for r in range(ROW_COUNT):
            if board[r][col] == 0:
                return r

    def winning_move(self, board, piece):
        # Check horizontal locations for win
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                    return True

        # Check positively sloped diagonals
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(COLUMN_COUNT - 3):
            for r in range(3, ROW_COUNT):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                    return True
        return False

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = PLAYER_PIECE
        if piece == PLAYER_PIECE:
            opp_piece = AI_PIECE

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, board, piece):
        score = 0

        # Score center column
        center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(ROW_COUNT):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(COLUMN_COUNT - 3):
                window = row_array[c:c + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(ROW_COUNT - 3):
                window = col_array[r:r + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(ROW_COUNT - 3):
            for c in range(COLUMN_COUNT - 3):
                window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        for r in range(ROW_COUNT - 3):
            for c in range(COLUMN_COUNT - 3):
                window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board):
        return self.winning_move(board, PLAYER_PIECE) or self.winning_move(board, AI_PIECE) or len(self.get_valid_locations(board)) == 0

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, AI_PIECE):
                    return None, 100000000000000
                elif self.winning_move(board, PLAYER_PIECE):
                    return None, -10000000000000
                else:  # Game is over, no more valid moves
                    return None, 0
            else:  # Depth is zero
                return None, self.score_position(board, AI_PIECE)
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, AI_PIECE)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else:  # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def get_valid_locations(self, board):
        valid_locations = []
        for col in range(COLUMN_COUNT):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

# Create a global game instance
game = Connect4Game()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/move', methods=['POST'])
def make_move():
    global game
    data = request.json
    col = data.get('column')
    difficulty = data.get('difficulty', 5)  # Default to medium difficulty if not specified
    
    if game.game_over:
        return jsonify({'error': 'Game is over', 'status': 'game_over'})
    
    # Player's move
    if not game.is_valid_location(game.board, col):
        return jsonify({'error': 'Invalid move', 'status': 'error'})
        
    row = game.get_next_open_row(game.board, col)
    game.drop_piece(game.board, row, col, PLAYER_PIECE)
    
    if game.winning_move(game.board, PLAYER_PIECE):
        game.game_over = True
        return jsonify({
            'status': 'win',
            'winner': 'player',
            'board': game.board.tolist()
        })

    # Check for draw after player's move
    if len(game.get_valid_locations(game.board)) == 0:
        game.game_over = True
        return jsonify({
            'status': 'draw',
            'board': game.board.tolist()
        })
        
    # AI's move
    ai_col, _ = game.minimax(game.board, difficulty, -math.inf, math.inf, True)
    if game.is_valid_location(game.board, ai_col):
        ai_row = game.get_next_open_row(game.board, ai_col)
        game.drop_piece(game.board, ai_row, ai_col, AI_PIECE)
        
        if game.winning_move(game.board, AI_PIECE):
            game.game_over = True
            return jsonify({
                'status': 'win',
                'winner': 'ai',
                'board': game.board.tolist(),
                'ai_move': ai_col
            })
            
        # Check for draw after AI's move
        if len(game.get_valid_locations(game.board)) == 0:
            game.game_over = True
            return jsonify({
                'status': 'draw',
                'board': game.board.tolist(),
                'ai_move': ai_col
            })
        
        return jsonify({
            'status': 'success',
            'board': game.board.tolist(),
            'ai_move': ai_col
        })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    global game
    game = Connect4Game()
    return jsonify({
        'status': 'success',
        'board': game.board.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080) 