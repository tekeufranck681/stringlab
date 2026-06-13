"""
Character Frequency Analysis  —  Analysis & Properties
======================================================

Count how many times each character appears in a string, and report a couple
of useful summaries: how many characters there are in total, and how many
*distinct* ones.

This is the foundation for many other string tasks — anagram checking, for
instance, is really just "do these two strings have the same frequency map?".

How it works — a single counting pass
--------------------------------------
Walk the string once. Keep a small table (a dictionary) mapping each character
to a running tally. Every character we land on bumps its tally by one.

Worked example for "banana":

        read 'b'  ->  {b:1}
        read 'a'  ->  {b:1, a:1}
        read 'n'  ->  {b:1, a:1, n:1}
        read 'a'  ->  {b:1, a:2, n:1}
        read 'n'  ->  {b:1, a:2, n:2}
        read 'a'  ->  {b:1, a:3, n:2}

    Result: counts = {b:1, a:3, n:2}, total = 6, distinct = 3

Complexity
----------
    Time  : O(n)  — one pass over the string, O(1) work per character.
    Space : O(k)  — `k` distinct characters stored in the table.

Standalone reference implementation (Python standard library only). Run it:

    python frequency.py
"""

from __future__ import annotations

from collections import Counter

COMPLEXITY = {"time": "O(n)", "space": "O(k)"}


def char_frequency(text: str) -> dict:
    """Return the per-character counts plus total and distinct summaries.

    `counts` is keyed by the character itself. We use `collections.Counter`,
    which is exactly a dictionary specialised for tallying — the manual loop in
    the module docstring is what it does under the hood.

    >>> char_frequency("banana") == {
    ...     "counts": {"b": 1, "a": 3, "n": 2},
    ...     "total": 6,
    ...     "distinct": 3,
    ... }
    True
    >>> char_frequency("")["distinct"]
    0
    """
    counts = Counter(text)

    return {
        "counts": dict(counts),   # plain dict for a clean, predictable result
        "total": len(text),       # every character counts, including spaces
        "distinct": len(counts),  # number of unique keys in the table
    }


def most_common(text: str, n: int = 1) -> list[tuple[str, int]]:
    """Return the `n` most frequent characters as (character, count) pairs.

    Handy for demos and for spotting the dominant symbol in a string.

    >>> most_common("banana", 2)
    [('a', 3), ('n', 2)]
    """
    return Counter(text).most_common(n)


def _demo() -> None:
    """Print a frequency table for a few curated examples."""
    examples = ["banana", "mississippi", "hello world", ""]

    print("Character Frequency Analysis")
    print("=" * 32)
    for text in examples:
        report = char_frequency(text)
        shown = repr(text) if text == "" else f'"{text}"'
        print(f"\n{shown}")
        print(f"    total = {report['total']}, distinct = {report['distinct']}")

        # Show the table sorted by count (high to low) for readability. The
        # sort is only for *display*; the algorithm itself does no sorting.
        for char, count in sorted(
            report["counts"].items(), key=lambda pair: pair[1], reverse=True
        ):
            label = "' '" if char == " " else f"'{char}'"
            bar = "█" * count
            print(f"    {label:<4} {count:>3}  {bar}")


if __name__ == "__main__":
    _demo()
