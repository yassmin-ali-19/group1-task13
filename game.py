import cv2
import numpy as np
from ultralytics import YOLO
import random
import time

# Load YOLOv8 model
model = YOLO('best.pt')  # Replace with your YOLO weights path

# Initialize game state
board = np.zeros((3, 3), dtype=int)
player_turn = 1  # Player 1 starts with 'X'
winner = None
game_mode = None  # None for menu, 1 for multiplayer, 2 for single-player
game_over = False
reset_timer = None  # Timer for automatic reset

# Function to reset the game state
def reset_game():
    global board, player_turn, winner, game_over, game_mode, reset_timer
    board = np.zeros((3, 3), dtype=int)
    player_turn = 1
    winner = None
    game_over = False
    game_mode = None
    reset_timer = None

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
    results = model.predict(source=frame, show=False, conf=0.7)
    detected_gesture = None
    bbox = None

    if results and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf, class_id = box.conf[0], int(box.cls[0])
            if class_id == 0:  # Assuming 0 is 'X'
                detected_gesture = 'X'
                bbox = (x1, y1, x2, y2)
                color = (255, 0, 0)  # Color for 'X'
            elif class_id == 1:  # Assuming 1 is 'O'
                detected_gesture = 'O'
                bbox = (x1, y1, x2, y2)
                color = (0, 255, 0)  # Color for 'O'

    return detected_gesture, bbox

# Function to get the grid position from gesture bounding box
def get_position_from_gesture(bbox):
    x1, y1, x2, y2 = bbox
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    grid_x = int(x_center // 300)
    grid_y = int(y_center // 300)
    return grid_x, grid_y

# AI move for single-player mode
def ai_move():
    empty_positions = np.argwhere(board == 0)
    if len(empty_positions) > 0:
        pos = empty_positions[random.choice(range(len(empty_positions)))]
        board[pos[0], pos[1]] = 2  # Computer makes a move (O)

# Main function
def main():
    global board, player_turn, winner, game_mode, game_over, reset_timer

    # Initialize video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (900, 900))

        if game_mode is None:
            gesture, _ = detect_gesture(frame)
            if gesture == 'X':
                game_mode = 2  # Single-player
            elif gesture == 'O':
                game_mode = 1  # Multiplayer

            cv2.putText(frame, 'Show X to play alone', (60, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 3)
            cv2.putText(frame, 'Show O to play with a friend', (60, 540), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 3)
            cv2.imshow("Tic-Tac-Toe", frame)

            if cv2.waitKey(1) == 27:  # Esc key to exit
                break
        else:
            if not game_over:  # Process gestures only if the game is not over
                gesture, bbox = detect_gesture(frame)
                if gesture and bbox:
                    x, y = get_position_from_gesture(bbox)
                    if x < 3 and y < 3 and board[y, x] == 0:
                        if player_turn == 1 and gesture == 'X':
                            board[y, x] = 1  # Player X makes a move
                            player_turn = 2
                        elif player_turn == 2 and gesture == 'O':
                            board[y, x] = 2  # Player O makes a move
                            player_turn = 1

            if game_mode == 2 and not game_over and player_turn == 2:  # AI's turn in single-player mode
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
                reset_timer = time.time()  # Start the timer for auto-reset
            else:
                cv2.putText(frame, f'Player {player_turn} turn', (230, 750), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)

            # Check if the reset timer has expired
            if game_over and reset_timer is not None and time.time() - reset_timer > 5:
                reset_game()

            # Check for manual reset button 'R'
            key = cv2.waitKey(1)
            if key == 27:  # Esc key to exit
                break
            elif key == ord('r') or key == ord('R'):  # Reset key
                reset_game()

            cv2.imshow("Tic-Tac-Toe", frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
