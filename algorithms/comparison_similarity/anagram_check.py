"""
Anagram Detection  —  Comparison & Similarity
=============================================

Two strings are *anagrams* if one is a rearrangement of the other — they use
exactly the same characters, the same number of times, just in a different
order. "listen" and "silent" are anagrams; so are "evil" and "vile".

How it works — compare the frequency maps
-----------------------------------------
Order does not matter, only *how many of each character* there is. So we count
characters in both strings (see analysis_properties/frequency.py) and check the
two tallies are identical:

    "listen"  ->  {l:1, i:1, s:1, t:1, e:1, n:1}
    "silent"  ->  {s:1, i:1, l:1, e:1, n:1, t:1}   same map -> anagrams ✓

    "rat"     ->  {r:1, a:1, t:1}
    "car"     ->  {c:1, a:1, r:1}                  't' vs 'c' differ -> not ✗

This comparison treats every character literally, including case and spaces, so
"Listen" and "silent" are NOT anagrams here ('L' != 'l'). Normalising case or
stripping spaces is a product decision left to the caller, keeping the algorithm
pure and predictable.

Complexity
----------
    Time  : O(n)  — count both strings in linear time, then compare maps.
    Space : O(k)  — `k` distinct characters held in the tallies.

Standalone reference implementation (Python standard library only). Run it:

    python anagram_check.py
"""

from __future__ import annotations

from collections import Counter

COMPLEXITY = {"time": "O(n)", "space": "O(k)"}


def anagram_check(source: str, target: str) -> dict:
    """Return whether `source` and `target` are anagrams of each other.

    A quick length check short-circuits the obvious non-anagrams: strings of
    different lengths can never be rearrangements of one another.

    >>> anagram_check("listen", "silent")["are_anagrams"]
    True
    >>> anagram_check("rat", "car")["are_anagrams"]
    False
    >>> anagram_check("abc", "abcd")["are_anagrams"]   # different lengths
    False
    """
    if len(source) != len(target):
        return {
            "are_anagrams": False,
            "explanation": (
                f"Lengths differ ({len(source)} vs {len(target)}), "
                "so they cannot be anagrams."
            ),
        }

    are_anagrams = Counter(source) == Counter(target)

    return {
        "are_anagrams": are_anagrams,
        "explanation": (
            "Both strings contain the same characters with the same counts."
            if are_anagrams
            else "The character counts differ, so they are not anagrams."
        ),
    }


def _demo() -> None:
    """Print the verdict for a few curated string pairs."""
    examples = [
        ("listen", "silent"),
        ("evil", "vile"),
        ("triangle", "integral"),
        ("rat", "car"),
        ("Listen", "silent"),  # case-sensitive: not anagrams here
    ]

    print("Anagram Detection — frequency-map comparison")
    print("=" * 44)
    for source, target in examples:
        outcome = anagram_check(source, target)
        verdict = "anagrams ✓" if outcome["are_anagrams"] else "not anagrams ✗"
        print(f'\n"{source}" vs "{target}" -> {verdict}')
        print(f"    {outcome['explanation']}")


if __name__ == "__main__":
    _demo()
