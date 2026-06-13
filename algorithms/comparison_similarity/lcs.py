"""
Longest Common Subsequence (LCS)  —  Comparison & Similarity
============================================================

A *subsequence* keeps characters in order but allows gaps — "ace" is a
subsequence of "abcde", but "aec" is not. The LCS of two strings is the longest
sequence that is a subsequence of *both*.

For "ABCBDAB" and "BDCAB" the LCS is "BCAB" (length 4). It is not necessarily
contiguous in either string, which is what separates this from "longest common
*substring*".

How it works — dynamic programming over a grid
----------------------------------------------
Build a table `dp` where `dp[i][j]` is the LCS length of the first `i`
characters of A and the first `j` characters of B:

    if A[i-1] == B[j-1]:
        dp[i][j] = dp[i-1][j-1] + 1         # extend the common run by one
    else:
        dp[i][j] = max(dp[i-1][j], dp[i][j-1])   # drop a char from one side

The bottom-right cell holds the LCS length; tracing the choices back from it
rebuilds the actual subsequence.

Worked grid for "ABCBDAB" (rows) vs "BDCAB" (cols), answer = 4:

            ""  B  D  C  A  B
        ""   0  0  0  0  0  0
        A    0  0  0  0  1  1
        B    0  1  1  1  1  2
        C    0  1  1  2  2  2
        B    0  1  1  2  2  3
        D    0  1  2  2  2  3
        A    0  1  2  2  3  3
        B    0  1  2  2  3  4   <- LCS length = 4

Complexity
----------
    Time  : O(n * m)  — one constant-time decision per grid cell.
    Space : O(n * m)  — the grid, retained so the subsequence can be traced.

Standalone reference implementation (Python standard library only). Run it:

    python lcs.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n*m)", "space": "O(n*m)"}


def lcs(source: str, target: str) -> dict:
    """Return the LCS length and one longest common subsequence.

    When several subsequences share the maximum length, this returns one valid
    answer (the one favoured by the trace-back rules below).

    >>> lcs("ABCBDAB", "BDCAB")["length"]
    4
    >>> lcs("ABCBDAB", "BDCAB")["subsequence"]
    'BCAB'
    >>> lcs("abc", "xyz")["length"]
    0
    """
    n, m = len(source), len(target)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Fill the grid; row 0 and column 0 stay 0 (an empty string shares nothing).
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if source[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    subsequence = _trace_back(source, target, dp)

    return {
        "length": dp[n][m],
        "subsequence": subsequence,
        "matrix": dp,
    }


def _trace_back(source: str, target: str, dp: list[list[int]]) -> str:
    """Rebuild one LCS by walking the grid from dp[n][m] back to the origin."""
    i, j = len(source), len(target)
    chars: list[str] = []

    while i > 0 and j > 0:
        if source[i - 1] == target[j - 1]:
            # This character is part of the LCS — take it and move diagonally.
            chars.append(source[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            # Move toward the larger neighbour (ties go up, by choice).
            i -= 1
        else:
            j -= 1

    chars.reverse()  # collected from the end, so flip to reading order
    return "".join(chars)


def _demo() -> None:
    """Print the LCS for a few curated string pairs."""
    examples = [
        ("ABCBDAB", "BDCAB"),
        ("AGGTAB", "GXTXAYB"),  # classic textbook pair -> "GTAB"
        ("hello", "world"),     # shares only "l" / "o" ordering -> length 1 or 2
        ("abc", "xyz"),         # nothing in common
    ]

    print("Longest Common Subsequence")
    print("=" * 28)
    for source, target in examples:
        outcome = lcs(source, target)
        print(
            f'\n"{source}" vs "{target}" -> '
            f'"{outcome["subsequence"]}" (length {outcome["length"]})'
        )


if __name__ == "__main__":
    _demo()
