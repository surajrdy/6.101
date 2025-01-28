"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!

# import string # optional import
# import pprint # optional import
# import typing # optional import
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        #TypeError
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        
        #Assinging an alias
        node = self
        #Iterate through the letters until we hit the word
        for i in range(len(key)):
            if key[i] not in node.children:
                node.children[key[i]] = PrefixTree()
            node = node.children[key[i]]
        node.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> tree = PrefixTree()
        >>> tree["cat"] = 1
        >>> tree["car"] = 2
        >>> tree["cat"]
        1
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        node = self

        #Check if the key is not in the prefix tree and update the node
        for i in range(len(key)):
            if key[i] not in node.children:
                raise KeyError("Given key is not in the prefix tree")
            node = node.children[key[i]]
        
        if node.value is None:
            raise KeyError("Given key is not in the prefix tree")
        
        #Return the final word
        return node.value
    
    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> tree = PrefixTree()
        >>> tree["cat"] = 1
        >>> tree["dog"] = 2
        >>> del tree["cat"]
        >>> "cat" in tree
        False
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        node = self
        #path = []
        for i in range(len(key)):
            if key[i] not in node.children:
                raise KeyError("Given key is not in the prefix tree")
            #path.append((node, key[i]))
            #No need for path as the delete doesn't require this
            node = node.children[key[i]]
            #Transitioning to the next node
        if node.value is None:
            raise KeyError("Given key is not in the prefix tree")
        node.value = None
        
        

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        >>> tree = PrefixTree()
        >>> tree["cat"] = 1
        >>> "cat" in tree
        True
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        node = self
        for char in key:
            #If it isn't then automatic False
            if char not in node.children:
                return False
            node = node.children[char]
        #Make sure the word exists
        return node.value is not None



    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        >>> tree = PrefixTree()
        >>> tree["cat"] = 1
        >>> tree["car"] = 2
        >>> tree["dog"] = 3
        >>> sorted(list(tree))
        [('car', 2), ('cat', 1), ('dog', 3)]
        """

        def helper(node, prev):
            if node.value is not None:
                yield (prev, node.value)
            for char, child in node.children.items():
                yield from helper(child, prev + char)
        
        yield from helper(self, "")
        


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    >>> text = "cat dog cat"
    >>> tree = word_frequencies(text)
    >>> tree["cat"]
    2
    """
    tree = PrefixTree()
    analysis = tokenize_sentences(text)
    for sent in analysis:
        #Splitting the sentence
        for word in sent.split():
            #Adding the word or if there is a key error keep at one
            try:
                tree[word] += 1
            except KeyError:
                tree[word] = 1
    return tree


            




def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    >>> tree = PrefixTree()
    >>> tree["cat"] = 5
    >>> tree["car"] = 3
    >>> tree["cart"] = 2
    >>> autocomplete(tree, "ca")
    ['cat', 'car', 'cart']
    """
    if not isinstance(prefix, str):
        raise TypeError("Prefix must be a string")
    results = []
    node = tree

    for char in prefix:
        if char in node.children:
            #Go to the next node
            node = node.children[char]
        else:
            #If this is not true, then we know there is not a result
            return []
    #Recursive helper function for pathing
    def pathing(node, path):
        #Iterate through while there is not a None value and append
        if node.value is not None:
            results.append((path, node.value))
        #Now check the currently made dictionary items and do the pathing again
        for char, child in node.children.items():
            pathing(child, path+char)
    #Apply function
    pathing(node, prefix)

    #Reverse order 
    results.sort(key = lambda x:-x[-1])

    #Simple list comp
    words = [word for word, _ in results]

    #Max_count parameter applied
    if max_count is not None:
        words = words[:max_count]

    return words

    



def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    >>> tree = PrefixTree()
    >>> tree["cat"] = 10
    >>> tree["car"] = 5
    >>> tree["cart"] = 3
    >>> autocorrect(tree, "cat")
    ['cat', 'car', 'cart']
    """
    #The initial autocomplete for our autocrrect structure
    initial = autocomplete(tree, prefix, max_count)

    #Have a present set to not repeat anything
    present = set(initial)

    #Combinations of all possible edits
    def edits(word):
        # Define the alphabet to use for letter replacements and insertions
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
        # Create all possible ways to split the word at every position
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        
        # Generate edits by deleting one character from each split
        deletions = [left + right[1:] for left, right in splits if right]
        
        # Generate edits by swapping adjacent characters
        transpositions = [left + right[1] + right[0] + right[2:] for left, right in splits if len(right) > 1]
        
        # Generate edits by replacing one character with each letter in the alphabet
        replacements = [left + letter + right[1:] for left, right in splits if right for letter in alphabet]
        
        # Generate edits by inserting each letter from the alphabet into each split position
        insertions = [left + letter + right for left, right in splits for letter in alphabet]
        
        # Return a set of all unique edits
        return set(deletions + transpositions + replacements + insertions)
    #Check for if we even need to do autocorrect and when to stop
    if max_count is None or len(initial) < max_count:

        #All posibilities
        poss = edits(prefix)

        results = []

        for ed in poss:
            try:
                #Check for duplicates
                if ed not in present:
                    results.append((ed, tree[ed]))
                    present.add(ed)
            except KeyError:
                continue
        #Sort by the order
        results.sort(key=lambda x:x[1])
        #print(results)
        combined = [wrd for wrd, _ in results]
        #Flip the combined list
        combined = combined[::-1]
        #print(combined)
        #Return the autocrrect
        if max_count is not None:
            combined = combined[:max_count - len(initial)]

        #Plus the initial
        return initial + combined
    #or return the initial
    return initial
         


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    results = []
    #Checking for already made
    done = set()
    def helper(node, index, so_far):
        # If we've reached the end of the pattern
        if index == len(pattern):
            # if it is a word, then add to the results
            if node.value is not None and so_far not in done:
                results.append((so_far, node.value))
                done.add(so_far)
            # if this occurs, then we keep going and run a seperate helper
            if pattern and pattern[-1] == '*':
                for char, node_c in node.children.items():
                    helper(node_c, index, so_far + char)
            return
        
        #Find the current character
        curr = pattern[index]
        
        # matching zero+ characters with the *
        if curr == '*':
            # move to the next character essentially, 1
            helper(node, index + 1, so_far)
            
            # explore the children nodes like a tree, 2
            for char, c_node in node.children.items():
                helper(c_node, index, so_far + char)

        # matching all possible characters with ?
        elif curr == '?':
            # iterate through each child node
            for char, c_node in node.children.items():
                helper(c_node, index + 1, so_far + char)

        # If there is only a single match case
        else:
            # if there is an exact match
            c_node = node.children.get(curr)
            if c_node:
                helper(c_node, index + 1, so_far + curr)
            else:
                # no match means a termination of the branch, backtrack
                return

    #Set up the helper now
    helper(tree, 0, "")
    return results


        





if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    doctest.run_docstring_examples( # runs doctests for one function
        PrefixTree.__getitem__,
        globals(),
        optionflags=_doctest_flags,
        verbose=True
     )
    with open("dracula.txt", encoding="utf-8") as f:
        text = f.read()
        t = word_frequencies(text)
        lis = autocomplete(t, "")
        print(len(lis))
        fil = word_filter(t, "")
        print(len(fil))
        aut = autocorrect(t, '')
        print(len(aut))
        total_words = sum(freq for _, freq in t)
        print(total_words)

