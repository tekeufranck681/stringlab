"""The computation engine (M3) — backend adaptations of the 12 algorithms.

Each builder takes an operation's (already-validated) ``inputs`` and returns a
``(result, explanation, trace)`` triple:

    result      a dict whose keys are exactly the contract's camelCase result
                keys (§9) — it is stored and returned verbatim as JSON.
    explanation a plain-language account of *this* run (FR-3.3).
    trace       a Trace for step_log/full operations, or None for result-level
                ones (contract §1.4, §3).

The traces follow the contract's TraceStep schema (§3): ``action`` + ``message``
plus an optional ``state`` snapshot and ``highlights`` carrying a *role* (the
frontend maps role -> colour; the backend never sends colours).

These differ on purpose from the standalone scripts in the repo-root
``algorithms/`` folder: those teach with simple steps, these emit the precise
animation contract the frontend renders.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Optional

from app.core.exceptions import AppException
from app.modules.computation.schemas import (
    CellRef,
    Highlight,
    MatrixState,
    SearchState,
    SequenceState,
    Trace,
    TraceAxes,
    TraceDimensions,
    TraceMeta,
    TraceStep,
)

# A builder maps inputs -> (result dict, explanation, trace-or-None).
Builder = Callable[[dict[str, Any]], tuple[dict[str, Any], str, Optional[Trace]]]


# ===========================================================================
# Analysis & Properties
# ===========================================================================
def _palindrome_check(inputs: dict[str, Any]):
    text = inputs["text"]
    left, right = 0, len(text) - 1
    is_palindrome = True
    while left < right:
        if text[left] != text[right]:
            is_palindrome = False
            break
        left += 1
        right -= 1

    explanation = (
        f'"{text}" reads the same forwards and backwards.'
        if is_palindrome
        else f'"{text}" is not a palindrome.'
    )
    return {"isPalindrome": is_palindrome}, explanation, None


def _char_frequency(inputs: dict[str, Any]):
    text = inputs["text"]
    counts: dict[str, int] = {}
    for char in text:  # preserve first-appearance order for a stable result
        counts[char] = counts.get(char, 0) + 1

    result = {"counts": counts, "total": len(text), "distinct": len(counts)}
    explanation = (
        f"{len(text)} characters in total, {len(counts)} of them distinct."
    )
    return result, explanation, None


def _longest_palindrome(inputs: dict[str, Any]):
    """step_log, family 'sequence' — expand-around-centre with a narrated trace."""
    text = inputs["text"]
    steps: list[TraceStep] = []

    def add(action, message, state=None, highlights=None):
        steps.append(
            TraceStep(
                index=len(steps), action=action, message=message,
                state=state, highlights=highlights,
            )
        )

    add("init", f'Searching "{text}" for its longest palindromic substring.')

    best_start, best_length = 0, (1 if text else 0)

    def expand(left: int, right: int) -> None:
        nonlocal best_start, best_length
        while left >= 0 and right < len(text) and text[left] == text[right]:
            add(
                "expand",
                f'"{text[left:right + 1]}" is a palindrome.',
                state=SequenceState(left=left, right=right, window=(left, right)),
                highlights=[Highlight(target="text", range=(left, right), role="match")],
            )
            if right - left + 1 > best_length:
                best_start, best_length = left, right - left + 1
            left -= 1
            right += 1

    for i in range(len(text)):
        expand(i, i)      # odd-length centre
        expand(i, i + 1)  # even-length centre

    substring = text[best_start : best_start + best_length]
    add(
        "done",
        f'Longest palindromic substring is "{substring}".',
        highlights=(
            [Highlight(target="text", range=(best_start, best_start + best_length - 1),
                       role="result")]
            if substring else None
        ),
    )

    result = {"substring": substring, "start": best_start, "length": best_length}
    trace = Trace(steps=steps, meta=TraceMeta(total_steps=len(steps), family="sequence"))
    return result, f'Found "{substring}" (length {best_length}).', trace


# ===========================================================================
# Search & Matching
# ===========================================================================
def _find_all_occurrences(inputs: dict[str, Any]):
    text, pattern = inputs["text"], inputs["pattern"]
    n, m = len(text), len(pattern)
    positions = [
        start
        for start in range(n - m + 1)
        if 0 < m <= n and text[start : start + m] == pattern
    ]
    explanation = (
        f'Found {len(positions)} occurrence(s) of "{pattern}".'
        if positions else f'"{pattern}" does not occur in the text.'
    )
    return {"positions": positions, "count": len(positions)}, explanation, None


def _count_occurrences(inputs: dict[str, Any]):
    text, pattern = inputs["text"], inputs["pattern"]
    n, m = len(text), len(pattern)
    count = sum(
        1
        for start in range(n - m + 1)
        if 0 < m <= n and text[start : start + m] == pattern
    )
    return {"count": count}, f'"{pattern}" occurs {count} time(s).', None


def _build_failure_table(pattern: str) -> list[int]:
    failure = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            failure[i] = length
            i += 1
        elif length > 0:
            length = failure[length - 1]
        else:
            failure[i] = 0
            i += 1
    return failure


def _kmp_search(inputs: dict[str, Any]):
    """full, family 'search' — KMP with a detailed comparison/jump trace."""
    text, pattern = inputs["text"], inputs["pattern"]
    n, m = len(text), len(pattern)
    failure = _build_failure_table(pattern) if m else []

    steps: list[TraceStep] = []

    def add(action, message, state=None, highlights=None):
        steps.append(
            TraceStep(index=len(steps), action=action, message=message,
                      state=state, highlights=highlights)
        )

    add(
        "init",
        f'Failure table for "{pattern}" computed as {failure}.',
        state=SearchState(text_index=0, pattern_index=0, shift=0,
                          comparisons=0, failure_table=failure),
    )

    positions: list[int] = []
    comparisons = 0
    i = j = 0
    if 0 < m <= n:
        while i < n:
            comparisons += 1
            compare_hl = [
                Highlight(target="text", index=i, role="compare"),
                Highlight(target="pattern", index=j, role="compare"),
            ]
            add(
                "compare",
                f"Compare text[{i}]={text[i]} with pattern[{j}]={pattern[j]}.",
                state=SearchState(text_index=i, pattern_index=j, shift=i - j,
                                  comparisons=comparisons),
                highlights=compare_hl,
            )
            if text[i] == pattern[j]:
                add(
                    "match", "Match — advance both.",
                    highlights=[
                        Highlight(target="text", index=i, role="match"),
                        Highlight(target="pattern", index=j, role="match"),
                    ],
                )
                i += 1
                j += 1
                if j == m:
                    start = i - j
                    positions.append(start)
                    add(
                        "found",
                        f"Full match at position {start}.",
                        state=SearchState(text_index=i - 1, pattern_index=j - 1,
                                          shift=start, comparisons=comparisons),
                        highlights=[Highlight(target="text", range=(start, i - 1),
                                              role="result")],
                    )
                    j = failure[j - 1]  # rewind to allow overlapping matches
            else:
                add(
                    "mismatch",
                    f"text[{i}]={text[i]} ≠ pattern[{j}]={pattern[j]}.",
                    state=SearchState(text_index=i, pattern_index=j, shift=i - j,
                                      comparisons=comparisons),
                    highlights=[
                        Highlight(target="text", index=i, role="mismatch"),
                        Highlight(target="pattern", index=j, role="mismatch"),
                    ],
                )
                if j > 0:
                    fallback = failure[j - 1]
                    add(
                        "jump",
                        f"Pattern index falls back to {fallback}; text index stays at {i}.",
                        state=SearchState(text_index=i, pattern_index=fallback,
                                          shift=i - fallback, comparisons=comparisons),
                    )
                    j = fallback
                else:
                    i += 1

    add("done", f"Found {len(positions)} occurrence(s) using {comparisons} comparisons.")

    result = {"positions": positions, "count": len(positions), "comparisons": comparisons}
    trace = Trace(steps=steps, meta=TraceMeta(total_steps=len(steps), family="search"))
    explanation = (
        f"Found {len(positions)} occurrence(s) at {positions} using "
        f"{comparisons} character comparisons."
    )
    return result, explanation, trace


# ===========================================================================
# Comparison & Similarity
# ===========================================================================
def _anagram_check(inputs: dict[str, Any]):
    source, target = inputs["source"], inputs["target"]
    are_anagrams = Counter(source) == Counter(target)
    explanation = (
        "Both strings contain the same characters with the same counts."
        if are_anagrams
        else "The character counts differ, so they are not anagrams."
    )
    return {"areAnagrams": are_anagrams}, explanation, None


def _edit_distance(inputs: dict[str, Any]):
    """full, family 'matrix' — DP grid fill plus a traced-back edit path."""
    source, target = inputs["source"], inputs["target"]
    n, m = len(source), len(target)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    steps: list[TraceStep] = []

    def add(action, message, state=None, highlights=None):
        steps.append(
            TraceStep(index=len(steps), action=action, message=message,
                      state=state, highlights=highlights)
        )

    add(
        "init", "Initialise the first row and column with 0..n.",
        highlights=[Highlight(target="cell", cell=CellRef(row=0, col=0), role="active")],
    )

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if source[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                choice = "match"
            else:
                diagonal, insert, delete = dp[i - 1][j - 1], dp[i][j - 1], dp[i - 1][j]
                best = min(diagonal, insert, delete)
                dp[i][j] = best + 1
                choice = (
                    "substitute" if best == diagonal
                    else "insert" if best == insert
                    else "delete"
                )
            add(
                "fill_cell", f"Cell ({i},{j}) = {dp[i][j]}.",
                state=MatrixState(cell=CellRef(row=i, col=j), value=dp[i][j], choice=choice),
                highlights=[Highlight(target="cell", cell=CellRef(row=i, col=j), role="active")],
            )

    operations, path = _edit_trace_back(source, target, dp)
    add(
        "trace_back",
        f"Optimal path traced: {dp[n][m]} edit(s).",
        highlights=[
            Highlight(target="cell", cell=CellRef(row=r, col=c), role="path")
            for r, c in path
        ],
    )

    result = {"distance": dp[n][m], "operations": operations}
    trace = Trace(
        steps=steps,
        meta=TraceMeta(
            total_steps=len(steps), family="matrix",
            axes=TraceAxes(row_label=source, col_label=target),
            dimensions=TraceDimensions(rows=n + 1, cols=m + 1),
        ),
    )
    return result, f"{dp[n][m]} edit(s) transform the source into the target.", trace


def _edit_trace_back(source, target, dp):
    """Return (operations, path-cells) walking dp[n][m] back to the origin."""
    i, j = len(source), len(target)
    operations: list[dict] = []
    path: list[tuple[int, int]] = [(i, j)]

    while i > 0 or j > 0:
        if i > 0 and j > 0 and source[i - 1] == target[j - 1]:
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            operations.append({"type": "substitute", "at": i - 1,
                               "from": source[i - 1], "to": target[j - 1]})
            i, j = i - 1, j - 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            operations.append({"type": "insert", "at": i, "char": target[j - 1]})
            j -= 1
        else:
            operations.append({"type": "delete", "at": i - 1, "char": source[i - 1]})
            i -= 1
        path.append((i, j))

    operations.reverse()
    path.reverse()
    return operations, path


def _lcs(inputs: dict[str, Any]):
    """step_log, family 'matrix' — LCS grid fill plus a traced-back path."""
    source, target = inputs["source"], inputs["target"]
    n, m = len(source), len(target)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    steps: list[TraceStep] = []

    def add(action, message, state=None, highlights=None):
        steps.append(
            TraceStep(index=len(steps), action=action, message=message,
                      state=state, highlights=highlights)
        )

    add("init", "Initialise the grid; an empty string shares nothing.")

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if source[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            add(
                "fill_cell", f"Cell ({i},{j}) = {dp[i][j]}.",
                state=MatrixState(cell=CellRef(row=i, col=j), value=dp[i][j]),
                highlights=[Highlight(target="cell", cell=CellRef(row=i, col=j), role="active")],
            )

    subsequence, path = _lcs_trace_back(source, target, dp)
    add(
        "trace_back",
        f'Longest common subsequence is "{subsequence}" (length {dp[n][m]}).',
        highlights=[
            Highlight(target="cell", cell=CellRef(row=r, col=c), role="path")
            for r, c in path
        ],
    )

    result = {"length": dp[n][m], "subsequence": subsequence}
    trace = Trace(
        steps=steps,
        meta=TraceMeta(
            total_steps=len(steps), family="matrix",
            axes=TraceAxes(row_label=source, col_label=target),
            dimensions=TraceDimensions(rows=n + 1, cols=m + 1),
        ),
    )
    return result, f'Longest common subsequence "{subsequence}" has length {dp[n][m]}.', trace


def _lcs_trace_back(source, target, dp):
    i, j = len(source), len(target)
    chars: list[str] = []
    path: list[tuple[int, int]] = []
    while i > 0 and j > 0:
        if source[i - 1] == target[j - 1]:
            chars.append(source[i - 1])
            path.append((i, j))
            i, j = i - 1, j - 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    chars.reverse()
    path.reverse()
    return "".join(chars), path


# ===========================================================================
# Transformation & Encoding
# ===========================================================================
_REVERSE_TRANSFORMS: dict[str, Callable[[str], str]] = {
    "reverse": lambda text: text[::-1],
    "upper": lambda text: text.upper(),
    "lower": lambda text: text.lower(),
    "title": lambda text: text.title(),
    "swapcase": lambda text: text.swapcase(),
}


def _reverse_transform(inputs: dict[str, Any]):
    text, mode = inputs["text"], inputs.get("mode", "reverse")
    output = _REVERSE_TRANSFORMS[mode](text)
    return {"output": output}, f"Applied '{mode}' to the input.", None


def _shift_letter(char: str, shift: int) -> str:
    if "a" <= char <= "z":
        base = ord("a")
    elif "A" <= char <= "Z":
        base = ord("A")
    else:
        return char
    return chr(base + (ord(char) - base + shift) % 26)


def _caesar_cipher(inputs: dict[str, Any]):
    text = inputs["text"]
    shift = int(inputs["shift"])
    mode = inputs.get("mode", "encode")
    effective = -(shift % 26) if mode == "decode" else shift % 26
    output = "".join(_shift_letter(char, effective) for char in text)
    explanation = f"{mode.capitalize()}d with a shift of {shift % 26}."
    return {"output": output, "shiftUsed": shift % 26}, explanation, None


def _run_length(inputs: dict[str, Any]):
    text, mode = inputs["text"], inputs.get("mode", "encode")
    if mode == "decode":
        output = _rle_decode(text)
        ratio = _space_savings(output, text)
        return {"output": output, "ratio": ratio}, "Expanded the encoded input.", None

    output = _rle_encode(text)
    ratio = _space_savings(text, output)
    return {"output": output, "ratio": ratio}, f"Encoded with {ratio} space saved.", None


def _rle_encode(text: str) -> str:
    if not text:
        return ""
    pieces, run_char, run_length = [], text[0], 1
    for char in text[1:]:
        if char == run_char:
            run_length += 1
        else:
            pieces.append(f"{run_char}{run_length}")
            run_char, run_length = char, 1
    pieces.append(f"{run_char}{run_length}")
    return "".join(pieces)


def _rle_decode(text: str) -> str:
    pieces, i = [], 0
    while i < len(text):
        char = text[i]
        i += 1
        digits = ""
        while i < len(text) and text[i].isdigit():
            digits += text[i]
            i += 1
        pieces.append(char * (int(digits) if digits else 1))
    return "".join(pieces)


def _space_savings(original: str, encoded: str) -> float:
    if not original:
        return 0.0
    return round(1 - len(encoded) / len(original), 2)


# ===========================================================================
# Dispatch
# ===========================================================================
BUILDERS: dict[str, Builder] = {
    "palindrome_check": _palindrome_check,
    "char_frequency": _char_frequency,
    "longest_palindrome": _longest_palindrome,
    "find_all_occurrences": _find_all_occurrences,
    "count_occurrences": _count_occurrences,
    "kmp_search": _kmp_search,
    "anagram_check": _anagram_check,
    "edit_distance": _edit_distance,
    "lcs": _lcs,
    "reverse_transform": _reverse_transform,
    "caesar_cipher": _caesar_cipher,
    "run_length": _run_length,
}


def run_operation(
    slug: str, inputs: dict[str, Any]
) -> tuple[dict[str, Any], str, Optional[Trace]]:
    """Execute the engine for `slug`. Inputs must already be validated.

    Raises AppException (500) if a catalogued operation has no engine
    implementation — a programming gap, not a user error.
    """
    builder = BUILDERS.get(slug)
    if builder is None:
        raise AppException(f"Operation '{slug}' has no computation implementation.")
    return builder(inputs)
