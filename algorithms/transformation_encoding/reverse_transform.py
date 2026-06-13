"""
Reversal & Case Transform  —  Transformation & Encoding
=======================================================

Produce a new string from an input by applying one simple, well-known rewrite.
Five modes are supported:

    reverse   -> characters in opposite order        "Hello" -> "olleH"
    upper     -> every letter uppercased             "Hello" -> "HELLO"
    lower     -> every letter lowercased             "Hello" -> "hello"
    title     -> first letter of each word uppercased"hello world" -> "Hello World"
    swapcase  -> upper<->lower swapped               "Hello" -> "hELLO"

Each mode maps to a battle-tested Python string operation, so the value here is
the clean, uniform interface — one function, a `mode` switch — rather than any
clever algorithm.

Complexity
----------
    Time  : O(n)  — every mode touches each character a constant number of times.
    Space : O(n)  — strings are immutable in Python, so a new string is built.

Standalone reference implementation (Python standard library only). Run it:

    python reverse_transform.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n)", "space": "O(n)"}

# The set of modes we accept, each paired with the transform it performs.
# Using a dispatch table keeps the function flat and makes the supported modes
# self-documenting and easy to extend.
_TRANSFORMS = {
    "reverse": lambda text: text[::-1],
    "upper": lambda text: text.upper(),
    "lower": lambda text: text.lower(),
    "title": lambda text: text.title(),
    "swapcase": lambda text: text.swapcase(),
}


def reverse_transform(text: str, mode: str = "reverse") -> dict:
    """Apply the rewrite named by `mode` to `text`.

    >>> reverse_transform("Hello", "reverse")["output"]
    'olleH'
    >>> reverse_transform("Hello World", "upper")["output"]
    'HELLO WORLD'
    >>> reverse_transform("hello world", "title")["output"]
    'Hello World'

    An unknown mode is a programming error here; the web layer validates `mode`
    against the allowed options before ever calling this.

    >>> reverse_transform("x", "rot13")
    Traceback (most recent call last):
        ...
    ValueError: Unknown mode 'rot13'; expected one of: lower, reverse, swapcase, title, upper
    """
    transform = _TRANSFORMS.get(mode)
    if transform is None:
        allowed = ", ".join(sorted(_TRANSFORMS))
        raise ValueError(f"Unknown mode '{mode}'; expected one of: {allowed}")

    return {"output": transform(text), "mode": mode}


def _demo() -> None:
    """Show every mode applied to a couple of sample strings."""
    samples = ["Hello World", "StringLab"]

    print("Reversal & Case Transform")
    print("=" * 26)
    for text in samples:
        print(f'\ninput: "{text}"')
        for mode in _TRANSFORMS:
            output = reverse_transform(text, mode)["output"]
            print(f"    {mode:<9} -> \"{output}\"")


if __name__ == "__main__":
    _demo()
