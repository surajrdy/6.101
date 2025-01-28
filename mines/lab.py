"""
6.101 Lab:
Mines
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    coordinates = (nrows, ncolumns)
    return new_game_nd(coordinates, mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """

    # Utilizing the dig_nd structure for the simple 2d cases
    coordinates = (row, col)
    return dig_nd(game, coordinates)


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    """board = game['board'][:]
    visible = game['visible']

    output = []
    #Ran into a problem with using just the output in the 
    # code, had to utilize two different copies
    for i, row in enumerate(board):
        new_row = []
        for j, col in enumerate(row):
            if all_visible or visible[i][j]:
                if col == 0:
                    new_row.append(' ')
                else:
                    new_row.append(str(col))
            else:
                new_row.append('_')
        output.append(new_row)
    
    return output"""
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    locations = render_nd(game, all_visible)
    # Starting string and then "append" the strings following
    output = ""
    for row in locations:
        for col in row:
            output += col
        output += "\n"
    return output[:-1]


def set_val(arr, coord, val):
    """
    Sets the value
    """
    for i in coord[:-1]:
        arr = arr[i]
    arr[coord[-1]] = val


def get_val(arr, coord):
    """
    Gets the value
    """
    for i in coord:
        arr = arr[i]
    return arr


# N-D IMPLEMENTATION


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    def create_nd_arr(dim, val):
        # Recursion base case
        if len(dim) == 1:
            return [val] * dim[0]
        result = []
        # Return the rest of the array creation
        for i in range(dim[0]):
            result.append(create_nd_arr(dim[1:], val))
        return result

    # Set value from the bac

    # Get the neighbor count
    def get_neighs(coord):
        # Recursive helper
        def helper(curr, index):
            # First yield case
            if index == len(coord):
                yield curr
            else:
                for change in (-1, 0, 1):
                    # Make copy to avoid problems
                    new_coord = curr[:]
                    new_coord[index] = coord[index] + change
                    # Checking for the boundaries
                    if new_coord[index] >= 0 and new_coord[index] < dimensions[index]:
                        # Recurse through the next dimensions now
                        for result in helper(new_coord, index + 1):
                            yield result

        # Using our helper function now
        neighbors = []
        for neigh in helper(list(coord), 0):
            if neigh != coord:
                neighbors.append(neigh)
        return neighbors

    # Utilizing the helper funcs now
    board = create_nd_arr(dimensions, 0)
    visible = create_nd_arr(dimensions, False)

    # Check for the mines, i'm having a problem here
    for mine in mines:
        # problem
        set_val(board, mine, ".")

    for coord in mines:
        for n in get_neighs(coord):
            # Check if it isn't a mine
            if get_val(board, n) != ".":
                # Use the neighbor count
                set_val(board, n, get_val(board, n) + 1)

    return {
        "dimensions": dimensions,
        "board": board,
        "visible": visible,
        "state": "ongoing",
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game["state"] != "ongoing":
        return 0

    # helper to get value from nested lists
    def get_value(board, coords):
        for c in coords:
            board = board[c]
        return board

    # Maybe I should put these in an outside function, but not sure about the referencing.
    # helper to set value in nested lists
    def set_value(board, coords, val):
        for c in coords[:-1]:
            board = board[c]
        board[coords[-1]] = val

    # function to get neighbors of a coordinate
    def get_neighbors(coord):
        neighbor_coords = []
        # build neighbor ranges for each dimension
        for i in range(len(coord)):
            neighbor_coords.append(
                range(
                    max(0, coord[i] - 1),
                    min(coord[i] + 1, game["dimensions"][i] - 1) + 1,
                )
            )
        # generating neighbor positions
        neighbors = []

        def generate_neighbors(index, current_coord):
            if index == len(neighbor_coords):
                # Need to convert to tuple, had problems
                neighbor = tuple(current_coord)
                if neighbor != coord:
                    # Checking for the neighrbors
                    neighbors.append(neighbor)
            else:
                for val in neighbor_coords[index]:
                    # I feel like this might be slightly inefficient, will check w/ TA
                    generate_neighbors(index + 1, current_coord + [val])

        generate_neighbors(0, [])
        return neighbors

    board = game["board"]
    visible = game["visible"]

    # check if already visible
    if get_value(visible, coordinates):
        return 0

    # For the squares revealed now, setting the visible part
    set_value(visible, coordinates, True)
    squares_revealed = 1

    # Getting the values of each of the boards
    cellVal = get_value(board, coordinates)

    if cellVal == ".":
        # Ending case
        game["state"] = "defeat"
        return squares_revealed

    # initialize safe cells remaining
    if "safe_cells_remaining" not in game:
        # compute total cells
        total = 1
        for d in game["dimensions"]:
            total *= d

        # count mines
        def count_mines(b):
            if isinstance(b, list):
                cnt = 0
                for elem in b:
                    cnt += count_mines(elem)
                return cnt
            else:
                if b == ".":
                    return 1
                else:
                    return 0

        mines = count_mines(board)

        # count revealed safe cells
        def count_revealed_safe(b, v):
            if isinstance(b, list):
                cnt = 0
                # Using zip function here, first
                for bb, vv in zip(b, v):
                    # Recursion
                    cnt += count_revealed_safe(bb, vv)
                return cnt
            else:
                if v and b != ".":
                    return 1
                else:
                    return 0

        revealed_safe = count_revealed_safe(board, visible)

        game["safe_cells_remaining"] = total - mines - revealed_safe

    else:
        # decrease safe cells remaining
        game["safe_cells_remaining"] -= 1

    # if the cell is empty, reveal neighbors
    if cellVal == 0:
        neighbors = get_neighbors(coordinates)
        for n in neighbors:
            if get_value(visible, n) == False:
                squares_revealed += dig_nd(game, n)

    # check victory condition
    if game["safe_cells_remaining"] == 0:
        game["state"] = "victory"

    return squares_revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    def render_cell(coord):
        content_value = get_value(game["board"], coord)
        # Checking all the edge cases
        if all_visible:
            cell_is_visible = True
        else:
            cell_is_visible = get_value(game["visible"], coord)
        if not cell_is_visible:
            return "_"
        else:
            if content_value == ".":
                return "."
            elif content_value == 0:
                return " "
            else:
                return str(content_value)

    def get_value(array, coord):
        # Maybe shuld abstract into a new function since its been used in all 3.
        for c in coord:
            array = array[c]
        return array

    def build_board(dimensions, coord_prefix=[]):
        # base to render the cell
        if len(dimensions) == 1:
            board = []
            for i in range(dimensions[0]):
                # Coor prefix being appended
                board.append(render_cell(coord_prefix + [i]))
            return board
        else:
            # resursion  build boards for each dimension
            board = []
            for i in range(dimensions[0]):
                # Check the rest
                board.append(build_board(dimensions[1:], coord_prefix + [i]))
            return board

    return build_board(game["dimensions"])


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    doctest.run_docstring_examples(
        render_2d_locations, globals(), optionflags=_doctest_flags, verbose=False
    )
