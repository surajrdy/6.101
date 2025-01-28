"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3


# Suraj Reddy Bacon Lab

import pickle

# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# REMEMBER THAT THE SET() IS NEEDED FOR EMPTY SET!!!!


def transform_data(raw_data):
    """
    Transforms the raw movie-actor dataset into a graph 
    so we can utilize it much easier.
    Args:
        raw_data: A list of tuples of the raw data from the .pickle files.
    Returns:
        output: A dictionary w/ actor graph, movie-actor mappings, and movies.
    """

    # Initialize the sets
    agraph = {}
    movies_actors = {}
    movies = {}

    # Looping through the tuple
    for a1, a2, mov in raw_data:
        # Adding values to the graph of actors
        if a1 not in agraph:
            agraph[a1] = set()
        if a2 not in agraph:
            agraph[a2] = set()
        agraph[a1].add(a2)
        agraph[a2].add(a1)
        # Setting the paths up
        if mov not in movies_actors:
            movies_actors[mov] = set()
        movies_actors[mov].update([a1, a2])

        # Adding the movie pairs for the movie_path functions
        pair = frozenset([a1, a2])
        movies.setdefault(pair, set()).add(mov)

    # Output dictionary which represents the transformed information

    output = {"agraph": agraph, "mov_act": movies_actors, "movies": movies}
    return output


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Returns a boolean value for if the actors have acted together
    Args:
        transformed_data: the transformed data from the raw data
        actor_id_1: ID of actor 1
        actor_id_2: ID of actor 2
    Returns:
        Boolean: True or False
    """
    # Checks for the edge case where they equal each other
    if actor_id_1 == actor_id_2:
        return True
    agraph = transformed_data["agraph"]

    return actor_id_2 in agraph.get(actor_id_1, set())

def actors_with_bacon_number(transformed_data, n):
    """
    Returns set of actors with the bacon number "n"
    Args:
        transformed_data: the transformed data from the raw data
        n: bacon number
    Returns:
        curr: set of the list of the bacon numbered actors
    """

    # Bacon ID
    bacon = 4724
    agraph = transformed_data["agraph"]
    # Essentially the visited values of the set
    done = set([bacon])
    # Current
    curr = set([bacon])
    # Edge case where we're looking for bacon
    if n == 0:
        if bacon in agraph:
            return {bacon}
        else:
            return set()

    # Arbitrary for loop
    for _ in range(n):
        # Next level for the BFS
        nxt = set()
        # Run BFS on the set
        for act in curr:
            neighbor = agraph.get(act, set())
            for neigh in neighbor:
                if neigh not in done:
                    done.add(neigh)
                    nxt.add(neigh)
        if not nxt:
            return set()
        # Set the current to the next_level
        curr = nxt
    return curr


def bacon_path(transformed_data, actor_id):
    # Simple usage of helper function
    return actor_to_actor_path(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    # Goal test function must be the actor_id_2
    return actor_path(transformed_data, actor_id_1, lambda x: x == actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Returns path of actors connected to each other
    Args:
        transformed_data: the transformed data from the raw data
        actor_id_1: the actor ID of the 1st actor
        goal_test_function: in our use case this will be actor_id_2
    Returns:
        path: path for the actors between each other
    """
    # Tests the edge case of the same actor id being used
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    # Graph of the actors
    agraph = transformed_data["agraph"]
    # Setting up the variables for the BFS
    done = set([actor_id_1])
    # Previously checked actors
    prev = {actor_id_1: None}
    curr = set([actor_id_1])
    while curr:
        # Next level
        nxt = set()
        for act in curr:
            neighbor = agraph.get(act, set())
            # BFS starts
            for neigh in neighbor:
                if neigh not in done:
                    done.add(neigh)
                    prev[neigh] = act
                    if goal_test_function(neigh):
                        path = [neigh]
                        while prev[path[-1]] is not None:
                            # Continue until we reach the starting 
                            # actor (where the previous actor is None)
                            path.append(prev[path[-1]])
                            # Append the previous actor to the path, 
                            # working backwards from the current actor
                        path.reverse()
                        return path
                    nxt.add(neigh)
        # Set current to the next level
        curr = nxt
    return None


def actors_connecting_films(transformed_data, film1, film2):
    """
    Returns the actors connected by film
    Args:
        transformed_data: the transformed data from the raw data
        film1: Film 1 ID
        film2: Film 2 ID
    Returns:
        path: path for the actors between each other
    """
    agraph = transformed_data["agraph"]
    movies_actors = transformed_data["mov_act"]

    a_film1 = movies_actors.get(film1, set())
    a_film2 = movies_actors.get(film2, set())

    if not a_film1 or not a_film2:
        return None

    # Using the set abilities to find the overlaps
    overlap = a_film1 & a_film2

    if overlap:
        act = overlap.pop()
        return [act]

    # BFS initialization

    done = set(a_film1)
    curr = set(a_film1)
    prev = {act: None for act in a_film1}

    while curr:
        nxt = set()
        for act in curr:
            neighbor = agraph.get(act, set())
            for neigh in neighbor:
                # BFS starts
                if (neigh in done) == False:
                    done.add(neigh)
                    prev[neigh] = act
                    if neigh in a_film2:
                        path = [neigh]
                        while prev[path[-1]] is not None:
                            # Continue until we reach the starting actor 
                            # (where the previous actor is None)
                            path.append(prev[path[-1]])
                            # Append the previous actor to the path, 
                            # working backwards from the current actor
                        path.reverse()
                        return path
                    nxt.add(neigh)
        curr = nxt
    return None


def get_actor_names(names_dict, actor_ids):
    # Help function to get the names of actors from the ID
    id_to_name = {id_: name for name, id_ in names_dict.items()}
    return [id_to_name.get(actor_id) for actor_id in actor_ids]


def movies_in_path(transformed_data, actor_id_1, actor_id_2):
    """
    Returns the movies that connect 2 actors
    Args:
        transformed_data: the 
        transformed data from the raw data
        actor_id_1: Actor 1
        actor_id_1: Actor 2
    Returns:
        movie_path: path for the movies between each other
    """
    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    if not path:
        return []  # No connection found for the movies
    movie_id = transformed_data.get("id_to_movie", {})
    p_movies = transformed_data["movies"]
    movie_path = []  # Use a separate list for movie names
    for i in range(len(path) - 1):
        a1 = path[i]
        a2 = path[i + 1]
        # Utilizing the frozenset here
        pair = frozenset([a1, a2])

        # Pairing the movies
        movies = p_movies.get(pair, set())

        # Choose one movie (if multiple, select arbitrarily)
        movie_id = next(iter(movies))
        movie_name = id_to_movie.get(movie_id)
        movie_path.append(movie_name)
    return movie_path


if __name__ == "__main__":
    with open("resources/names.pickle", "rb") as g:
        names = pickle.load(g)
    id_to_name = {id_: name for name, id_ in names.items()}
    with open("resources/large.pickle", "rb") as f:
        smalldb = pickle.load(f)
    with open("resources/movies.pickle", "rb") as h:
        movies = pickle.load(h)
    transformed = transform_data(smalldb)
    # Invert the movies mapping to create ID to movie name mapping
    id_to_movie = {id_: name for name, id_ in movies.items()}
    transformed["id_to_movie"] = id_to_movie
