"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """

    # Simplified representation of the game state with a dictionary
    # containing the board and the player's position
    game_state = {
        "board": level_description,
        "player_position": None,
    }
    # Find the player's position on the board
    for i, row in enumerate(level_description):
        # Iterate through the rows and columns to find the player's position
        for j, col in enumerate(row):
            # Check if the current position contains the player
            if "player" in col:
                # Update the player's position in the game state variable dict.
                game_state["player_position"] = (i, j)
                break
    return game_state


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """

    # First, we need to check if the edge case where
    # there are no targets or computers is true.
    targets = 0
    computers = 0

    for row in game["board"]:
        for col in row:
            if "target" in col:
                targets += 1
            if "computer" in col:
                computers += 1
    # If there are no target, then we know it is impossible to win.
    if targets == 0 or computers == 0:
        return False

    # If there exists a target w/o a computer, the game is not won yet.
    for row in game["board"]:
        for col in row:
            if "target" in col and "computer" not in col:
                return False

    # If we have checked all the false conditions, we know the game is won.
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    new_game = {
        "board": [list(map(list, row)) for row in game["board"]],
        "player_position": game["player_position"],
    }
    # Position of the player
    player_pos = game["player_position"]
    # Below contains the row and column of the player's next move.
    d_row, d_col = DIRECTION_VECTOR[direction]
    # This is the proposed position of the player after the move, not confirmed yet.
    new_row, new_col = player_pos[0] + d_row, player_pos[1] + d_col

    # The following if statements contain information on
    # whether the proposed move is valid.
    if (
        new_row < 0
        or new_row >= len(new_game["board"])
        or new_col < 0
        or new_col >= len(new_game["board"][0])
    ):
        # The above checks if the player is even in the board.
        return new_game
    # The below checks if the player is moving into a wall.
    if "wall" in new_game["board"][new_row][new_col]:
        return new_game
    # The below checks if the player is moving into a computer.
    if "computer" in new_game["board"][new_row][new_col]:
        # Attempting to push the computer
        next_row, next_col = new_row + d_row, new_col + d_col
        if (
            next_row < 0
            or next_row >= len(new_game["board"])
            or next_col < 0
            or next_col >= len(new_game["board"][0])
            or "wall" in new_game["board"][next_row][next_col]
            or "computer" in new_game["board"][next_row][next_col]
        ):
            return new_game
        # If none of the above is true, we know we can do the move.
        else:
            new_game["board"][next_row][next_col].append("computer")
            new_game["board"][new_row][new_col].remove("computer")

    # Remove the old player position and add the new one.
    new_game["board"][player_pos[0]][player_pos[1]].remove("player")
    new_game["board"][new_row][new_col].append("player")
    new_game["player_position"] = (new_row, new_col)

    return new_game


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    # Since we utilized a simple dictionary, we can just return the board itself!
    dump = game["board"]
    return dump


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    # Utilize a queue for the BFS and a visited set.
    queue = [(game, [])]
    visited = set()
    visited.add(tuple((i, j, tuple(sorted(game["board"][i][j]))) for i in range(len(game["board"])) for j in range(len(game["board"][0]))))
    

    # While our queue is not empty, we will pop the first element.
    while queue:
        current_game, path = queue.pop(0)
        # If the first element is the winning condition, we return this.
        if victory_check(current_game):
            return path
        # Now we need to check all the other possibilities.
        for direction in DIRECTION_VECTOR.keys():
            # Make a new game w/ the step_game function
            new_game = step_game(current_game, direction)

            # Create the new board state.
            new_board_state = tuple(
                tuple(tuple(sorted(cell)) for cell in row)
                for row in new_game["board"]
                # List comprehension to create a tuple of tuples.
            )
            # Check if the new board state hasn't visited.
            if new_board_state not in visited:
                # Add the board to the visited set now.
                visited.add(new_board_state)
                queue.append((new_game, path + [direction]))
    # If there is no solution, we return None.
    return None


if __name__ == "__main__":
    pass
