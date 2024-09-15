import cv2
import numpy as np
import torch
import random

# Load YOLO model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='path_to_yolo_weights.pt')  # Replace with your YOLO weights path(mina)

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
        cv2.line(img, (i * 300, 0), (i * 300, 900), (255, 255, 255), 6)
        cv2.line(img, (0, i * 300), (900, i * 300), (255, 255, 255), 6)

# Function to draw X and O on the board
def draw_XO(img, board):
    for i in range(3):
        for j in range(3):
            if board[i, j] == 1:
                cv2.putText(img, 'X', (j * 300 + 90, i * 300 + 210), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 0, 0), 15)
            elif board[i, j] == 2:
                cv2.putText(img, 'O', (j * 300 + 90, i * 300 + 210), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 255, 0), 15)

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

# YOLO Detection function
def detect_gesture(frame):
    results = model(frame)
    for result in results.xyxy[0]:
        x1, y1, x2, y2, conf, class_id = result
        class_id = int(class_id)
        if class_id == 'X':  # Assuming 0 is 'X'(mina)
            return 'X'
        elif class_id == 'O':  # Assuming 1 is 'O'(mina)
            return 'O'
    return None

# Function to get the grid position from gesture bounding box
def get_position_from_gesture(result):
    x1, y1, x2, y2 = result[:4]
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    grid_x = int(x_center // 300)
    grid_y = int(y_center // 300)
    return grid_x, grid_y

def ai_move():
    empty_positions = np.argwhere(board == 0)
    if len(empty_positions) > 0:
        pos = empty_positions[random.choice(range(len(empty_positions)))]
        board[pos[0], pos[1]] = 2  # Computer makes a move (O)

# Initialize video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (900, 900))

    if game_mode is None:
        gesture = detect_gesture(frame)
        if gesture:
            if gesture == 'X':
                game_mode = 2  # Single-player
            elif gesture == 'O':
                game_mode = 1  # Multiplayer

        cv2.putText(frame, 'Show 🤞 to play alone', (60, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 3)
        cv2.putText(frame, 'Show 👌 to play with a friend', (60, 540), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 3)
        cv2.imshow("Tic-Tac-Toe", frame)

        if cv2.waitKey(1) == 27:  # Esc key to exit
            break
    else:
        results = model(frame)
        gesture = None
        for result in results.xyxy[0]:
            class_id = int(result[5])
            if class_id == 0:  # Assuming 0 is 'X'
                gesture = 'X'
                x, y = get_position_from_gesture(result)
                if x < 3 and y < 3 and board[y, x] == 0:
                    if game_mode == 1 or player_turn == 1:
                        board[y, x] = 1
                        player_turn = 2
            elif class_id == 1:  # Assuming 1 is 'O'
                gesture = 'O'
                x, y = get_position_from_gesture(result)
                if x < 3 and y < 3 and board[y, x] == 0:
                    if game_mode == 1 or player_turn == 2:
                        board[y, x] = 2
                        player_turn = 1

        if game_mode == 2 and not game_over and player_turn == 2:  # Computer's turn
            ai_move()
            player_turn = 1
            winner = check_winner(board)

        draw_board(frame)
        draw_XO(frame, board)

        if winner is not None:
            if winner == -1:
                cv2.putText(frame, 'Draw!', (250, 750), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, f'Player {winner} wins!', (150, 750), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            game_over = True
        else:
            cv2.putText(frame, f'Player {player_turn} turn', (230, 750), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)

        cv2.imshow("Tic-Tac-Toe", frame)

        if cv2.waitKey(1) == 27:  # Esc key to exit
            break

cap.release()
cv2.destroyAllWindows()
