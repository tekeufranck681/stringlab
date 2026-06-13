"""
Find All Occurrences  —  Search & Matching
==========================================

Report *every* starting position where a pattern appears inside a text.
Occurrences may overlap: searching "aa" inside "aaaa" finds matches at
positions 0, 1 and 2.

How it works — the naive sliding window
---------------------------------------
Line the pattern up against the text at position 0, compare character by
character; if every pattern character matches, record the position. Then slide
the pattern one step to the right and try again, until the pattern would run
off the end of the text.

Worked example — pattern "ab" inside "abcab":

        text:    a b c a b
        pos 0:   a b              "ab" == "ab"  -> match at 0
        pos 1:     b c            'b' != 'a'    -> no match
        pos 2:       c a          'c' != 'a'    -> no match
        pos 3:         a b        "ab" == "ab"  -> match at 3
                                  pos 4 would overflow -> stop

    Result: positions = [0, 3], count = 2

This naive method is simple and perfectly good for short inputs. The smarter
Knuth-Morris-Pratt search (see kmp_search.py) avoids re-checking characters and
runs in linear time — compare the two to see the payoff.

Complexity
----------
    Time  : O(n * m)  — up to (n - m + 1) alignments, each up to m comparisons.
    Space : O(1)      — aside from the list of positions we return.

Standalone reference implementation (Python standard library only). Run it:

    python find_all_occurrences.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n*m)", "space": "O(1)"}


def find_all_occurrences(text: str, pattern: str) -> dict:
    """Return every (overlapping) start index where `pattern` occurs in `text`.

    A pattern that is empty, or longer than the text, simply yields zero
    occurrences — both are valid, not errors.

    >>> find_all_occurrences("abcab", "ab")["positions"]
    [0, 3]
    >>> find_all_occurrences("aaaa", "aa")["positions"]   # overlaps are counted
    [0, 1, 2]
    >>> find_all_occurrences("abc", "xyz")["positions"]
    []
    """
    n, m = len(text), len(pattern)
    positions: list[int] = []

    if m == 0 or m > n:
        return {"positions": [], "count": 0}

    # Try every alignment where the whole pattern still fits inside the text.
    for start in range(n - m + 1):
        # text[start:start + m] is the window the pattern is sitting over.
        if text[start : start + m] == pattern:
            positions.append(start)

    return {"positions": positions, "count": len(positions)}


def _demo() -> None:
    """Print matches for a few curated (text, pattern) pairs."""
    examples = [
        ("abcabcabc", "abc"),
        ("aaaa", "aa"),          # overlapping matches
        ("mississippi", "issi"), # also overlaps: positions 1 and 4
        ("hello", "z"),          # no match
        ("hi", "hello"),         # pattern longer than text
    ]

    print("Find All Occurrences — naive sliding window")
    print("=" * 44)
    for text, pattern in examples:
        outcome = find_all_occurrences(text, pattern)
        print(f'\ntext="{text}"  pattern="{pattern}"')
        print(f"    positions = {outcome['positions']}, count = {outcome['count']}")


if __name__ == "__main__":
    _demo()
