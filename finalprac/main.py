def swap_pairs(inp):
    if len(inp) < 2:
        return inp
    return [inp[1], inp[0], swap_pairs(inp[2:])]