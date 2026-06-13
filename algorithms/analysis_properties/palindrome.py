"""
Palindrome Detection  —  Analysis & Properties
==============================================

A *palindrome* is a string that reads the same forwards and backwards.
Classic examples: "level", "radar", "noon", "abba".

How we detect one — the two-pointer technique
----------------------------------------------
Instead of building the reversed string and comparing (which costs extra
memory), we walk inwards from both ends at the same time:

    - `left`  starts at the first character (index 0)
    - `right` starts at the last  character (index n - 1)
    - compare the pair, then step `left` right and `right` left
    - the instant a pair disagrees, it cannot be a palindrome

Worked example for "radar":

        index:   0 1 2 3 4
        chars:   r a d a r
                 ^       ^      compare r == r  -> ok, move inward
                   ^   ^        compare a == a  -> ok, move inward
                     ^          left meets right in the middle -> palindrome

Worked example for "hello" (fails fast):

        index:   0 1 2 3 4
        chars:   h e l l o
                 ^       ^      compare h == o  -> mismatch, stop -> not a palindrome

Complexity
----------
    Time  : O(n)  — in the worst case each character is inspected once.
    Space : O(1)  — only two integer indices; no reversed copy is made.

This is a standalone reference implementation (Python standard library only).
Run it directly to see the worked examples:

    python palindrome.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n)", "space": "O(1)"}


def is_palindrome(text: str) -> bool:
    """Return True if `text` reads the same forwards and backwards.

    This is the lean version: just the yes/no answer, no narration.

    >>> is_palindrome("level")
    True
    >>> is_palindrome("hello")
    False
    >>> is_palindrome("a")        # a single character is trivially a palindrome
    True
    >>> is_palindrome("")         # so is the empty string
    True
    """
    left, right = 0, len(text) - 1

    while left < right:
        # The moment the mirrored characters disagree we have our answer.
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1

    # The pointers crossed without ever disagreeing -> it's a palindrome.
    return True


def check_palindrome(text: str) -> dict:
    """Detect a palindrome AND record each comparison as a teaching step.

    The returned `steps` list is what a learner (or a UI step-log) can replay
    to *see* the two pointers walking inward. Each step captures the pair of
    characters that were compared and whether they matched.

    >>> check_palindrome("abba")["result"]
    True
    >>> check_palindrome("abca")["result"]
    False
    """
    left, right = 0, len(text) - 1
    steps: list[dict] = []

    while left < right:
        matched = text[left] == text[right]

        # Record this comparison before we react to it.
        steps.append(
            {
                "left": left,
                "right": right,
                "left_char": text[left],
                "right_char": text[right],
                "matched": matched,
            }
        )

        if not matched:
            return {
                "result": False,
                "explanation": (
                    f"'{text[left]}' (position {left}) and "
                    f"'{text[right]}' (position {right}) differ, "
                    f"so \"{text}\" is not a palindrome."
                ),
                "steps": steps,
            }

        left += 1
        right -= 1

    return {
        "result": True,
        "explanation": f'"{text}" reads the same forwards and backwards.',
        "steps": steps,
    }


def _demo() -> None:
    """Print a friendly walkthrough using a few curated examples."""
    examples = ["level", "radar", "hello", "abba", "Noon", "a", ""]

    print("Palindrome Detection — two-pointer walkthrough")
    print("=" * 48)
    for text in examples:
        outcome = check_palindrome(text)
        verdict = "palindrome ✓" if outcome["result"] else "not a palindrome ✗"
        shown = repr(text) if text == "" else f'"{text}"'
        print(f"\n{shown:<10} -> {verdict}")
        for step in outcome["steps"]:
            mark = "==" if step["matched"] else "!="
            print(
                f"    compare [{step['left']}]'{step['left_char']}' "
                f"{mark} [{step['right']}]'{step['right_char']}'"
            )
        print(f"    {outcome['explanation']}")

    # A note worth seeing: "Noon" is NOT a palindrome here because the check is
    # case-sensitive ('N' != 'n'). Normalising case/spacing is a product
    # decision, deliberately left to the caller so the algorithm stays pure.


if __name__ == "__main__":
    _demo()
