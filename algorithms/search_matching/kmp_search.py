"""
Knuth-Morris-Pratt (KMP) Search  —  Search & Matching  [FLAGSHIP]
================================================================

Find every position where a pattern occurs in a text in *linear* time, O(n + m).
The naive search (see find_all_occurrences.py) re-examines text characters after
a mismatch; KMP never does. That single idea is what makes it fast — and what
ties it to the theory of computation: the precomputed table turns the pattern
into a deterministic finite automaton that scans the text without backtracking.

The key idea — the failure table (a.k.a. LPS)
---------------------------------------------
For each prefix of the pattern we precompute the length of the longest *proper*
prefix that is also a suffix of that prefix ("proper" = not the whole thing).
This `failure[k]` tells us: if we mismatch after matching k characters, how many
of them we can keep without re-reading the text.

Failure table for pattern "ABAB":

        prefix      longest proper prefix == suffix     failure value
        "A"         (none)                              0
        "AB"        (none)                              0
        "ABA"       "A"                                 1
        "ABAB"      "AB"                                2

    => failure = [0, 0, 1, 2]

Why it helps — a mismatch becomes a jump, not a restart
-------------------------------------------------------
Searching "ABAB" in "ABABCABAB":

        text:    A B A B C A B A B
                 A B A B                matched 4 chars, then C != next
                                        instead of restarting at text[1],
                                        failure[3] = 2 says "2 chars still valid"
        text:    A B A B C A B A B
                     A B . .            resume comparing pattern[2] vs text[4]

The text pointer never moves backwards — each character is compared a bounded
number of times, giving the linear bound.

Complexity
----------
    Time  : O(n + m)  — O(m) to build the table, O(n) to scan the text.
    Space : O(m)      — the failure table, one entry per pattern character.

Standalone reference implementation (Python standard library only). Run it:

    python kmp_search.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n+m)", "space": "O(m)"}


def build_failure_table(pattern: str) -> list[int]:
    """Compute the KMP failure table (longest-proper-prefix-suffix lengths).

    >>> build_failure_table("ABAB")
    [0, 0, 1, 2]
    >>> build_failure_table("AAAA")
    [0, 1, 2, 3]
    >>> build_failure_table("ABCD")
    [0, 0, 0, 0]
    """
    m = len(pattern)
    failure = [0] * m

    # `length` is the length of the current longest prefix-that-is-also-suffix.
    length = 0
    i = 1  # failure[0] is always 0, so start filling from index 1

    while i < m:
        if pattern[i] == pattern[length]:
            # The prefix got one character longer — record and advance.
            length += 1
            failure[i] = length
            i += 1
        elif length > 0:
            # Fall back to the previous candidate prefix and try again WITHOUT
            # advancing i. This is the same trick the search loop uses.
            length = failure[length - 1]
        else:
            # No prefix-suffix here at all.
            failure[i] = 0
            i += 1

    return failure


def kmp_search(text: str, pattern: str) -> dict:
    """Find all (overlapping) occurrences of `pattern` in `text` using KMP.

    Returns the match `positions`, their `count`, the number of character
    `comparisons` performed (the headline efficiency metric), the
    `failure_table`, and a `steps` list narrating the scan.

    >>> kmp_search("ABABCABAB", "ABAB")["positions"]
    [0, 5]
    >>> kmp_search("aaaa", "aa")["positions"]   # overlaps are reported
    [0, 1, 2]
    >>> kmp_search("abc", "xyz")["count"]
    0
    """
    n, m = len(text), len(pattern)

    if m == 0 or m > n:
        return {
            "positions": [],
            "count": 0,
            "comparisons": 0,
            "failure_table": build_failure_table(pattern) if m else [],
            "steps": [],
        }

    failure = build_failure_table(pattern)
    positions: list[int] = []
    steps: list[dict] = []
    comparisons = 0

    i = 0  # index into the text    — only ever moves forward
    j = 0  # index into the pattern — rewinds via the failure table

    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            # Characters agree: advance through both text and pattern.
            steps.append(
                {
                    "action": "match",
                    "text_index": i,
                    "pattern_index": j,
                    "comparisons": comparisons,
                }
            )
            i += 1
            j += 1

            if j == m:
                # The whole pattern matched, ending at text index i - 1.
                start = i - j
                positions.append(start)
                steps.append(
                    {
                        "action": "found",
                        "position": start,
                        "comparisons": comparisons,
                    }
                )
                # Rewind j (not i) so overlapping matches are still found.
                j = failure[j - 1]
        elif j > 0:
            # Mismatch after some progress: jump the pattern back using the
            # failure table instead of moving the text pointer back.
            steps.append(
                {
                    "action": "jump",
                    "text_index": i,
                    "from_pattern_index": j,
                    "to_pattern_index": failure[j - 1],
                    "comparisons": comparisons,
                }
            )
            j = failure[j - 1]
        else:
            # Mismatch at the very start of the pattern: just advance the text.
            steps.append(
                {
                    "action": "mismatch",
                    "text_index": i,
                    "pattern_index": j,
                    "comparisons": comparisons,
                }
            )
            i += 1

    return {
        "positions": positions,
        "count": len(positions),
        "comparisons": comparisons,
        "failure_table": failure,
        "steps": steps,
    }


def _demo() -> None:
    """Show the failure table and matches for a few curated examples."""
    examples = [
        ("ABABCABAB", "ABAB"),
        ("ABABDABACDABABCABAB", "ABABCABAB"),  # forces several failure-table jumps
        ("aaaa", "aa"),                         # overlapping matches
        ("abcdef", "xyz"),                      # no match
    ]

    print("Knuth-Morris-Pratt Search [FLAGSHIP]")
    print("=" * 40)
    for text, pattern in examples:
        outcome = kmp_search(text, pattern)
        print(f'\ntext="{text}"')
        print(f'pattern="{pattern}"  failure_table={outcome["failure_table"]}')
        print(
            f"    positions = {outcome['positions']}, "
            f"count = {outcome['count']}, "
            f"comparisons = {outcome['comparisons']}"
        )
        # Highlight how many character comparisons the naive method would have
        # needed in the worst case, to make the linear-time win tangible.
        n, m = len(text), len(pattern)
        naive_worst = (n - m + 1) * m if n >= m else 0
        print(f"    (naive worst case would be up to {naive_worst} comparisons)")


if __name__ == "__main__":
    _demo()
