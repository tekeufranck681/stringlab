"""
Levenshtein Edit Distance  —  Comparison & Similarity  [FLAGSHIP]
================================================================

The edit distance between two strings is the minimum number of single-character
edits — *insert*, *delete*, or *substitute* — needed to turn one into the other.
Turning "kitten" into "sitting" takes 3 edits, so their distance is 3.

How it works — dynamic programming over a grid
----------------------------------------------
Build a table `dp` where `dp[i][j]` is the edit distance between the first `i`
characters of the source and the first `j` characters of the target. Each cell
is decided from three neighbours already computed:

    if source[i-1] == target[j-1]:
        dp[i][j] = dp[i-1][j-1]                    # characters match, free move
    else:
        dp[i][j] = 1 + min(
            dp[i-1][j-1],   # substitute
            dp[i][j-1],     # insert
            dp[i-1][j],     # delete
        )

The first row/column are the base cases: turning a string into "" costs one
delete per character (and vice-versa for inserts).

Worked grid for "kitten" -> "sitting" (answer is the bottom-right cell = 3):

            ""  s  i  t  t  i  n  g
        ""   0  1  2  3  4  5  6  7
        k    1  1  2  3  4  5  6  7
        i    2  2  1  2  3  4  5  6
        t    3  3  2  1  2  3  4  5
        t    4  4  3  2  1  2  3  4
        e    5  5  4  3  2  2  3  4
        n    6  6  5  4  3  3  2  3   <- distance = 3

We then *trace back* from the bottom-right corner, following the choices that
produced each cell, to recover the actual list of edits.

Complexity
----------
    Time  : O(n * m)  — one constant-time decision per grid cell.
    Space : O(n * m)  — the full grid (kept so we can trace the path back).

Standalone reference implementation (Python standard library only). Run it:

    python edit_distance.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n*m)", "space": "O(n*m)"}


def edit_distance(source: str, target: str) -> dict:
    """Return the Levenshtein distance, the edit operations, and the DP grid.

    `operations` lists the concrete edits that transform `source` into `target`,
    in left-to-right order, each tagged with its position.

    >>> edit_distance("kitten", "sitting")["distance"]
    3
    >>> edit_distance("", "abc")["distance"]    # three inserts
    3
    >>> edit_distance("abc", "abc")["distance"] # identical strings
    0
    """
    n, m = len(source), len(target)

    # dp has (n + 1) rows and (m + 1) columns to include the empty-prefix bases.
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Base cases: distance from a prefix to the empty string is its length.
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    # Fill the grid row by row, each cell from its three neighbours.
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if source[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # match: carry the diagonal across
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],  # substitute
                    dp[i][j - 1],      # insert
                    dp[i - 1][j],      # delete
                )

    operations = _trace_back(source, target, dp)

    return {
        "distance": dp[n][m],
        "operations": operations,
        "matrix": dp,
    }


def _trace_back(source: str, target: str, dp: list[list[int]]) -> list[dict]:
    """Walk from dp[n][m] back to dp[0][0], collecting the edits taken.

    At each step we ask "which neighbour did this cell come from?" and record the
    matching edit. We collect edits back-to-front, then reverse them so the
    result reads left-to-right.
    """
    i, j = len(source), len(target)
    operations: list[dict] = []

    while i > 0 or j > 0:
        if i > 0 and j > 0 and source[i - 1] == target[j - 1]:
            # Characters already match — a free diagonal move, no edit recorded.
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            operations.append(
                {
                    "type": "substitute",
                    "at": i - 1,
                    "from": source[i - 1],
                    "to": target[j - 1],
                }
            )
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            operations.append(
                {"type": "insert", "at": i, "char": target[j - 1]}
            )
            j -= 1
        else:  # came from above -> a deletion
            operations.append(
                {"type": "delete", "at": i - 1, "char": source[i - 1]}
            )
            i -= 1

    operations.reverse()  # we built it from the end; flip to reading order
    return operations


def _render_matrix(source: str, target: str, dp: list[list[int]]) -> str:
    """Return the DP grid as a labelled, human-readable string (for the demo)."""
    header = "       " + "  ".join(["''", *target])
    lines = [header]
    row_labels = ["''", *source]
    for i, row in enumerate(dp):
        cells = "  ".join(f"{value:>2}" for value in row)
        lines.append(f"    {row_labels[i]:>2} {cells}")
    return "\n".join(lines)


def _demo() -> None:
    """Show the grid and the recovered edits for a few curated pairs."""
    examples = [
        ("kitten", "sitting"),
        ("flaw", "lawn"),
        ("", "abc"),
        ("same", "same"),
    ]

    print("Levenshtein Edit Distance [FLAGSHIP]")
    print("=" * 40)
    for source, target in examples:
        outcome = edit_distance(source, target)
        print(f'\n"{source}" -> "{target}"   distance = {outcome["distance"]}')
        if source and target:
            print(_render_matrix(source, target, outcome["matrix"]))
        if outcome["operations"]:
            print("    edits:")
            for op in outcome["operations"]:
                if op["type"] == "substitute":
                    print(f"      substitute '{op['from']}' -> '{op['to']}' at {op['at']}")
                elif op["type"] == "insert":
                    print(f"      insert '{op['char']}' at {op['at']}")
                else:
                    print(f"      delete '{op['char']}' at {op['at']}")
        else:
            print("    (no edits needed — strings are identical)")


if __name__ == "__main__":
    _demo()
