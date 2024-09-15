**YOLO-Based Tic-Tac-Toe Game Code**

1. Overview:

This code integrates YOLO object detection with a Tic-Tac-Toe game. It uses a YOLO model to detect gestures for game control, allowing users to play in either single-player (against the computer) or multiplayer modes.

2. Code Structure:

-Initializing Libraries:

Cv2 , numpy , torch , random

-Initialize Game State:

Game State Variables: Initializes the game board and variables to track the game state and player turns.

-Functions: 

        reset_game(): Resets the game to its initial state.
        
        draw_board(img): Draws the Tic-Tac-Toe grid on the frame.
        
         draw_XO(img, board): Draws 'X' or 'O' on the board based on the game state.
         
        check_winner(board): Checks if there is a winner or if the game is a draw.
        
        detect_gesture(frame): Detects gestures from the video frame and returns 'X' or 'O'.
        
         get_position_from_gesture(result): Converts gesture bounding box coordinates to grid positions.
         
         ai_move(): Makes a random move for the AI in single-player mode.
         
-Main Loop:

The main loop handles game logic, including gesture detection, player moves, AI moves, and displaying the game state. It captures video frames, processes them for gesture detection, updates the game board, and displays the current state of the game.
