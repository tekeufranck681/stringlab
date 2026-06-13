"""
Run-Length Encoding (RLE)  —  Transformation & Encoding
=======================================================

A small but genuine lossless compression scheme: replace each *run* of identical
characters with the character followed by how many times it repeats.

    encode "aaabbc"   -> "a3b2c1"     (a x3, b x2, c x1)
    decode "a3b2c1"   -> "aaabbc"     (the exact inverse)

RLE shines on data with long repeats (think simple bitmap images or "aaaaaa")
and can actually *grow* data with no repeats ("abc" -> "a1b1c1"). That trade-off
is the whole point of measuring a compression ratio.

How it works
------------
Encoding: walk the string, count consecutive equal characters, and emit
`char + count` whenever the run ends. Decoding: read a character, read the digits
that follow it as the repeat count, and expand.

Assumption: the input to *encode* contains no digits, because digits are how the
encoded form stores counts — mixing them in would make decoding ambiguous. The
web layer restricts the alphabet accordingly.

Complexity
----------
    Time  : O(n)  — a single pass to encode, a single pass to decode.
    Space : O(n)  — the produced string.

Standalone reference implementation (Python standard library only). Run it:

    python run_length.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n)", "space": "O(n)"}


def _space_savings(original: str, encoded: str) -> float:
    """Fraction of size saved by the encoding — the standard RLE quality metric.

        savings = 1 - (compressed_length / original_length)

    A positive value means the data shrank (e.g. 0.67 means it is 67% smaller);
    0.0 means no change; a *negative* value means the encoding grew the data,
    which RLE does on inputs with no repeats ("abc" -> "a1b1c1").

    Returns 0.0 for an empty input to avoid dividing by zero.

    >>> _space_savings("aaaaaa", "a6")   # 6 chars -> 2 chars
    0.67
    >>> _space_savings("aaabbc", "a3b2c1")  # 6 -> 6, no gain
    0.0
    >>> _space_savings("abc", "a1b1c1")  # 3 -> 6, it grew
    -1.0
    """
    if not original:
        return 0.0
    return round(1 - len(encoded) / len(original), 2)


def encode(text: str) -> dict:
    """Run-length encode `text`.

    >>> encode("aaabbc")["output"]
    'a3b2c1'
    >>> encode("aaaaaa")["output"]    # great case for RLE
    'a6'
    >>> encode("abc")["output"]       # worst case: output is longer
    'a1b1c1'
    """
    if not text:
        return {"output": "", "ratio": 0.0, "mode": "encode"}

    pieces: list[str] = []
    run_char = text[0]
    run_length = 1

    # Compare each character with the one before it; when the run breaks, flush.
    for char in text[1:]:
        if char == run_char:
            run_length += 1
        else:
            pieces.append(f"{run_char}{run_length}")
            run_char = char
            run_length = 1
    pieces.append(f"{run_char}{run_length}")  # flush the final run

    output = "".join(pieces)
    return {
        "output": output,
        "ratio": _space_savings(text, output),
        "mode": "encode",
    }


def decode(text: str) -> dict:
    """Expand a run-length encoded string back to its original form.

    Counts may be multi-digit, so "a12" correctly expands to twelve a's.

    >>> decode("a3b2c1")["output"]
    'aaabbc'
    >>> decode("a12")["output"]
    'aaaaaaaaaaaa'
    >>> decode("")["output"]
    ''
    """
    pieces: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]      # the symbol of this run
        i += 1

        # Read the run of digits that encodes the repeat count.
        digits = ""
        while i < n and text[i].isdigit():
            digits += text[i]
            i += 1

        # A symbol with no following count is treated as a single occurrence.
        count = int(digits) if digits else 1
        pieces.append(char * count)

    output = "".join(pieces)
    return {
        "output": output,
        "ratio": _space_savings(output, text),
        "mode": "decode",
    }


def run_length(text: str, mode: str = "encode") -> dict:
    """Dispatch to encode/decode based on `mode` (the uniform entry point)."""
    if mode == "encode":
        return encode(text)
    if mode == "decode":
        return decode(text)
    raise ValueError(f"Unknown mode '{mode}'; expected 'encode' or 'decode'.")


def _demo() -> None:
    """Encode a few samples and confirm decoding round-trips back."""
    examples = ["aaabbc", "aaaaaa", "abc", "wwwwaaadexxxxxx"]

    print("Run-Length Encoding")
    print("=" * 20)
    for text in examples:
        encoded = encode(text)
        restored = decode(encoded["output"])["output"]
        print(f'\n"{text}"')
        print(f"    encode -> \"{encoded['output']}\"  (ratio {encoded['ratio']})")
        print(f"    decode -> \"{restored}\"  (round-trips: {restored == text})")


if __name__ == "__main__":
    _demo()
