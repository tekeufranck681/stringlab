"""
Occurrence Counter  —  Search & Matching
=========================================

Report *how many times* a pattern appears inside a text. This is the lighter
sibling of "find all occurrences": when you only need the tally and not the
exact positions, you can skip storing the list.

Overlapping matches count
-------------------------
We count overlapping occurrences, so "aa" appears 3 times in "aaaa":

        text:    a a a a
        pos 0:   a a            match  (1)
        pos 1:     a a          match  (2)
        pos 2:       a a        match  (3)

    Result: count = 3

Note this differs from Python's built-in ``"aaaa".count("aa")``, which returns
2 because it counts *non-overlapping* matches. We deliberately count overlaps so
the tally agrees with find_all_occurrences.

Complexity
----------
    Time  : O(n * m)  — same scan as the naive search, we just don't store hits.
    Space : O(1)      — a single running counter.

Standalone reference implementation (Python standard library only). Run it:

    python count_occurrences.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n*m)", "space": "O(1)"}


def count_occurrences(text: str, pattern: str) -> dict:
    """Return how many times `pattern` occurs in `text`, counting overlaps.

    An empty pattern, or one longer than the text, yields a count of zero.

    >>> count_occurrences("aaaa", "aa")["count"]   # overlaps counted
    3
    >>> count_occurrences("abcabc", "abc")["count"]
    2
    >>> count_occurrences("abc", "xyz")["count"]
    0
    """
    n, m = len(text), len(pattern)

    if m == 0 or m > n:
        return {"count": 0}

    count = 0
    # Check every alignment; bump the counter on each full match. We never store
    # the positions, which is the whole point of the lighter counter.
    for start in range(n - m + 1):
        if text[start : start + m] == pattern:
            count += 1

    return {"count": count}


def _demo() -> None:
    """Print the tally for a few curated (text, pattern) pairs."""
    examples = [
        ("aaaa", "aa"),
        ("abcabcabc", "abc"),
        ("banana", "ana"),   # overlapping: positions 1 and 3 -> count 2
        ("hello", "l"),
        ("hello", "z"),
    ]

    print("Occurrence Counter (overlapping matches)")
    print("=" * 40)
    for text, pattern in examples:
        outcome = count_occurrences(text, pattern)
        print(f'text="{text}"  pattern="{pattern}"  ->  count = {outcome["count"]}')


if __name__ == "__main__":
    _demo()
