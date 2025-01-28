"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import sys

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Finds a satisfying assignment for a given CNF formula.
    Returns the assignment as a dictionary if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> T, F = True, False
    >>> x = satisfying_assignment([[('a', T), ('b', F), ('c', T)]])
    >>> x.get('a', None) is T or x.get('b', None) is F or x.get('c', None) is T
    True
    >>> satisfying_assignment([[('a', T)], [('a', F)]])  # Unsatisfiable formula
    """
    # Start with an empty assignment and begin the recursive search
    assignment = {}
    result = recursive_sat(formula, assignment)
    return result


def recursive_sat(formula, assignment):
    """
    Recursive helper function to find a satisfying assignment.

    Args:
        formula: The CNF formula represented as a list of clauses.
        assignment: Current variable assignments.

    Returns:
        A satisfying assignment if one exists, or None.
    """
    # Simplify the formula based on the current assignments
    # if theres none left then it will be a not
    simplified_formula = simplify_formula(formula, assignment)

    # Recursion base cases
    if simplified_formula is None:
        return None
    # If all clauses are satisfied
    if not simplified_formula:
        return assignment

    # unit clause to find a single clause
    uclaus = find_uclaus(simplified_formula)
    while uclaus:
        for clause in uclaus:
            var, val = clause[0]
            # check for any conflicts
            if var in assignment and assignment[var] != val:
                return None  # The opposite
            assignment[var] = val  # Assign the variable
        # simplying the formula
        simplified_formula = simplify_formula(simplified_formula, assignment)
        if simplified_formula is None:
            return None  # contradiction
        if not simplified_formula:
            return assignment  # everything is sat.
        uclaus = find_uclaus(simplified_formula)

    # check for the most frequent variable
    variables = {var for clause in simplified_formula for var, _ in clause}
    unassigned_vars = variables - assignment.keys()
    # If there are no other unass but the simpl form is not none, then it is invalid
    if not unassigned_vars:
        return None
    # finding the chosen w/ helper
    chosen_var = select_variable(simplified_formula, unassigned_vars)

    # assign false
    assignment_copy = assignment.copy()
    assignment_copy[chosen_var] = False
    result = recursive_sat(simplified_formula, assignment_copy)
    if result is not None:
        return result

    # assign true
    assignment_copy = assignment.copy()
    assignment_copy[chosen_var] = True
    result = recursive_sat(simplified_formula, assignment_copy)
    if result is not None:
        return result

    # return none if all else fails
    return None


def simplify_formula(formula, assignment):
    """
    Simplifies the CNF formula.

    Args:
        formula: list of clauses.
        assignment: variable assignments.

    Returns:
        A simplified formula or None if a contradiction is found.
    """
    # empty list
    simplified_formula = []
    for clause in formula:
        new_clause = []
        satisf = False
        for var, val in clause:
            if var in assignment:
                if assignment[var] == val:
                    # the clause is satisfied by the current assignment
                    satisf = True
                    break  # We don't need to check others
            else:
                # unassigned literals for future iterations
                new_clause.append((var, val))
        if not satisf:
            if not new_clause:
                # this is a contradiction then
                return None
            simplified_formula.append(new_clause)
    return simplified_formula


def find_uclaus(formula):
    """
    Finds clauses of length 1.

    Args:
        formula: The formula.

    Returns:
        list of unit clauses.
    """
    # simple list comprehension
    return [clause for clause in formula if len(clause) == 1]


def select_variable(formula, unassigned_vars):
    """
    Selects the most used variable.

    Args:
        formula: The CNF formula.
        unassigned_vars: unassigned variables.

    Returns:
        The selected var
    """
    counts = {var: 0 for var in unassigned_vars}
    # everything starts at 0
    for clause in formula:
        for var, _ in clause:
            if var in unassigned_vars:
                counts[var] += 1
    return max(counts, key=counts.get)


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Produces a CNF formula for the scheduling problem.

    Args:
        student_preferences: dict mapping students.
        room_capacities: dict mapping constraints.

    Returns:
        A CNF formula.
    """
    cnf = []
    students = list(student_preferences.keys())
    rooms = list(room_capacities.keys())

    # 1 Assigning the students to their room
    for stud in students:
        preferred = student_preferences[stud]
        for room in rooms:
            # As per the lab
            var = f"{stud}_{room}"
            if room not in preferred:
                # Student cannot be in this room
                cnf.append([(var, False)])

    # 2: Then we check because each student has to be in atleast one room
    for stud in students:
        possible_assignments = []
        for room in student_preferences[stud]:
            var = f"{stud}_{room}"
            possible_assignments.append((var, True))
        cnf.append(possible_assignments)

    # 3: The student's can't be in two rooms at once
    for stud in students:
        preferred = list(student_preferences[stud])
        for i in range(len(preferred)):
            for j in range(i + 1, len(preferred)):
                var1 = f"{stud}_{preferred[i]}"
                var2 = f"{stud}_{preferred[j]}"
                # At most one of these variables can be True
                cnf.append([(var1, False), (var2, False)])

    # 4: capacity can't be reached
    for room in rooms:
        capacity = room_capacities[room]
        # vairables of all the preferences
        students_in_room = [
            f"{stud}_{room}" for stud in students if room in student_preferences[stud]
        ]
        if len(students_in_room) > capacity:
            # combinations of student's that exceed the list
            excess_combinations = generate_combinations(students_in_room, capacity + 1)
            for combo in excess_combinations:
                # At least one student in this combination cannot be in the room
                cnf.append([(var, False) for var in combo])

    return cnf


def generate_combinations(elements, k):
    """
    Generates all the combinations

    Args:
        elements: A list of elements
        k: capacity

    Returns:
        A list of combinations
    """
    result = []

    # Backtracking algo
    def backtrack(start, combo):
        if len(combo) == k:
            result.append(combo[:])
            return
        for i in range(start, len(elements)):
            combo.append(elements[i])
            # recurse
            backtrack(i + 1, combo)
            # Why is changing it from -1 to nothing more efficient?
            combo.pop()

    # initiatlize the recursion
    backtrack(0, [])
    return result


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
