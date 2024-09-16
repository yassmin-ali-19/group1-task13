import cv2
import numpy as np
import random

# Initialize game state
board = np.zeros((3, 3), dtype=int)
player_turn = 1  # Player 1 starts with 'X'
winner = None
game_mode = None  # None for menu, 1 for multiplayer, 2 for single-player
selected_position = None
game_over = False  # Track if the game has ended

# Function to reset the game state
def reset_game():
    global board, player_turn, winner, game_over, game_mode
    board = np.zeros((3, 3), dtype=int)
    player_turn = 1  # Player 1 starts with 'X'
    winner = None
    game_over = False
    game_mode = None  # Go back to the game mode selection screen

# Function to draw the Tic-Tac-Toe board
def draw_board(img):
    for i in range(1, 3):
        cv2.line(img, (i * 200, 0), (i * 200, 600), (255, 255, 255), 6)
        cv2.line(img, (0, i * 200), (600, i * 200), (255, 255, 255), 6)

# Function to draw X and O on the board
def draw_XO(img, board):
    for i in range(3):
        for j in range(3):
            if board[i, j] == 1:
                cv2.putText(img, 'X', (j * 200 + 60, i * 200 + 140), cv2.FONT_HERSHEY_SIMPLEX, 4, (145, 44, 118), 12)
            elif board[i, j] == 2:
                cv2.putText(img, 'O', (j * 200 + 60, i * 200 + 140), cv2.FONT_HERSHEY_SIMPLEX, 4, (119, 4, 223), 12)

# Function to check for a winner
def check_winner(board):
    for i in range(3):
        if np.all(board[i, :] == board[i, 0]) and board[i, 0] != 0:
            return board[i, 0]
        if np.all(board[:, i] == board[0, i]) and board[0, i] != 0:
            return board[0, i]
    if board[0, 0] == board[1, 1] == board[2, 2] != 0:
        return board[0, 0]
    if board[0, 2] == board[1, 1] == board[2, 0] != 0:
        return board[0, 2]
    if np.all(board != 0):
        return -1  # Draw
    return None

# Function for AI to make a random move
def ai_move():
    empty_positions = np.argwhere(board == 0)
    if len(empty_positions) > 0:
        pos = empty_positions[random.choice(range(len(empty_positions)))]
        board[pos[0], pos[1]] = 2  # Computer makes a move (O)

# Simulated gesture detection function using keyboard input
def detect_gesture():
    key = cv2.waitKey(1)
    if key == ord('x'):  # Simulate 🤞 gesture for "X"
        return 'X'
    elif key == ord('o'):  # Simulate 👌 gesture for "O"
        return 'O'
    return None

# Mouse click callback to get grid position
def select_grid_position(event, x, y, flags, param):
    global selected_position
    if event == cv2.EVENT_LBUTTONDOWN and not game_over:  # Only allow selection if the game is not over
        selected_position = (x // 200, y // 200)  # Map click to grid

# Function to get position from mouse click
def get_position_from_gesture():
    global selected_position
    if selected_position:
        pos = selected_position
        selected_position = None
        return pos
    return None

# Initialize video capture
cap = cv2.VideoCapture(0)

# Set up mouse callback
cv2.namedWindow("Tic-Tac-Toe")
cv2.setMouseCallback("Tic-Tac-Toe", select_grid_position)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (600, 600))  # Resize to 600x600

    if game_mode is None:
        gesture = detect_gesture()
        if gesture:
            if gesture == 'X':
                game_mode = 2  # Single-player
            elif gesture == 'O':
                game_mode = 1  # Multiplayer

        cv2.putText(frame, 'Press "x" to play alone', (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (40, 38, 210), 3)
        cv2.putText(frame, 'Press "o" to play with a friend', (50, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (40, 38, 210), 3)
        cv2.imshow("Tic-Tac-Toe", frame)

        if cv2.waitKey(1) == 27:  # Esc key to exit
            break
    else:
        if not game_over:
            gesture = detect_gesture()
            if gesture:
                pos = get_position_from_gesture()
                if pos is not None and pos[0] < 3 and pos[1] < 3 and board[pos[1], pos[0]] == 0:
                    if gesture == 'X' and (game_mode == 1 or player_turn == 1):
                        if player_turn == 1:  # Check if it's player 1's turn
                            board[pos[1], pos[0]] = 1  # Player 1 makes a move (X)
                            player_turn = 2  # Switch to player 2
                            winner = check_winner(board)
                    elif gesture == 'O' and (game_mode == 1 or player_turn == 2):
                        if player_turn == 2:  # Check if it's player 2's turn
                            board[pos[1], pos[0]] = 2  # Player 2 makes a move (O)
                            player_turn = 1  # Switch to player 1
                            winner = check_winner(board)

            if game_mode == 2 and not game_over and player_turn == 2:  # Computer's turn
                ai_move()
                player_turn = 1  # Switch back to player 1
                winner = check_winner(board)

            draw_board(frame)
            draw_XO(frame, board)

            if winner is not None:
                game_over = True  # Mark the game as over
                if winner == -1:
                    cv2.putText(frame, 'Draw!', (170, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                else:
                    cv2.putText(frame, f'Player {winner} wins!', (110, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (95, 0, 255), 3)

                cv2.imshow("Tic-Tac-Toe", frame)
                cv2.waitKey(1000)  # Wait for 1 second before restarting the game
                reset_game()
            else:
                cv2.putText(frame, f'Player {player_turn} turn', (150, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (119, 176, 145), 3)

        # Check for restart key press
        if cv2.waitKey(1) == ord('r'):
            reset_game()

        cv2.imshow("Tic-Tac-Toe", frame)

        if cv2.waitKey(1) == 27:  # Esc key to exit
            break

cap.release()
cv2.destroyAllWindows()
