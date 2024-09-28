import creversi
import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("color", choices=["black", "white"])
    args = parser.parse_args()

    if args.color == "black":
        color = creversi.BLACK_TURN
    else:
        color = creversi.WHITE_TURN

    # game loop
    while True:
        board_line = input()
        if not board_line:
            break
        board = creversi.Board(board_line, color)
        legal_moves = [move for move in range(64) if board.is_legal(move)]
        if len(legal_moves) == 0:
            raise ValueError("No legal moves")
        move = np.random.choice(legal_moves)
        print(move)


if __name__ == "__main__":
    main()
