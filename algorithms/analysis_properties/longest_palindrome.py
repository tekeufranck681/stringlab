"""
Longest Palindromic Substring  —  Analysis & Properties
=======================================================

Given a string, find the longest *contiguous* slice of it that is itself a
palindrome. For "babad" the answer is "bab" (or "aba" — both are length 3).

How it works — expand around centre
-----------------------------------
Every palindrome has a centre and grows outward symmetrically. So we try every
possible centre and push outward as far as the mirror still holds:

    - For odd-length palindromes the centre is a single character: (i, i).
          a b a   -> centre 'b', expands to "aba"
    - For even-length palindromes the centre sits *between* two characters: (i, i+1).
          a b b a -> centre between the two 'b's, expands to "abba"

For each centre we move `left` outward and `right` outward while the characters
still match, remembering the widest palindrome seen so far.

Worked example for "cbbd":

        centre (1,1) 'b'      -> "b"
        centre (1,2) 'b''b'   -> "bb"   <- new best (length 2)
        centre (2,2) 'b'      -> "b"
        ...
    Result: "bb", start = 1, length = 2

Why two kinds of centre? A single string can hide palindromes of both parities
("noon" is even, "racecar" is odd), so we check 2n - 1 possible centres in all.

Complexity
----------
    Time  : O(n^2) — n centres, each expansion is O(n) in the worst case.
    Space : O(1)   — we only track indices; the result is sliced out at the end.

Standalone reference implementation (Python standard library only). Run it:

    python longest_palindrome.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n^2)", "space": "O(1)"}


def longest_palindrome(text: str) -> dict:
    """Find the longest palindromic substring and narrate the expansions.

    Returns the winning `substring`, where it `start`s, its `length`, and a
    `steps` list recording every successful one-character expansion (useful for
    a step-log replay).

    >>> longest_palindrome("babad")["substring"] in {"bab", "aba"}
    True
    >>> longest_palindrome("cbbd")["substring"]
    'bb'
    >>> longest_palindrome("")["length"]
    0
    """
    if not text:
        return {"substring": "", "start": 0, "length": 0, "steps": []}

    # Track the best palindrome found so far by its start index and length.
    best_start, best_length = 0, 1
    steps: list[dict] = []

    def expand(left: int, right: int) -> None:
        """Grow outward from a centre while the mirror holds; record each hit."""
        nonlocal best_start, best_length

        while left >= 0 and right < len(text) and text[left] == text[right]:
            current_length = right - left + 1

            steps.append(
                {
                    "left": left,
                    "right": right,
                    "substring": text[left : right + 1],
                    "length": current_length,
                }
            )

            # A wider palindrome wins; ties keep the first one found.
            if current_length > best_length:
                best_start, best_length = left, current_length

            left -= 1   # step the left edge further out...
            right += 1  # ...and the right edge too, staying symmetric

    for i in range(len(text)):
        expand(i, i)      # odd-length centre: the character at i
        expand(i, i + 1)  # even-length centre: the gap between i and i+1

    return {
        "substring": text[best_start : best_start + best_length],
        "start": best_start,
        "length": best_length,
        "steps": steps,
    }


def _demo() -> None:
    """Print the winning substring for a few curated examples."""
    examples = ["babad", "cbbd", "racecar", "abacdfgdcaba", "a", ""]

    print("Longest Palindromic Substring — expand around centre")
    print("=" * 52)
    for text in examples:
        outcome = longest_palindrome(text)
        shown = repr(text) if text == "" else f'"{text}"'
        print(
            f"\n{shown:<14} -> \"{outcome['substring']}\" "
            f"(start={outcome['start']}, length={outcome['length']})"
        )
        # Show only the expansions that grew past a single character, so the
        # interesting growth is visible without drowning in trivial length-1 hits.
        for step in outcome["steps"]:
            if step["length"] > 1:
                print(
                    f"    found \"{step['substring']}\" "
                    f"spanning [{step['left']}..{step['right']}]"
                )


if __name__ == "__main__":
    _demo()
