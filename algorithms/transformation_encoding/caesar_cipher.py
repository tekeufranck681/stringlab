"""
Caesar Cipher  —  Transformation & Encoding
===========================================

The Caesar cipher shifts every letter a fixed number of places along the
alphabet, wrapping around from Z back to A. With a shift of 3, 'A' becomes 'D'
and 'Z' becomes 'C'. Decoding simply shifts the other way.

It is named after Julius Caesar, who reputedly used a shift of 3 for his private
correspondence. It is trivially breakable today, but it is a perfect, tangible
illustration of *modular arithmetic* — the "wrap around" is `mod 26`.

How it works — shift within the alphabet, modulo 26
---------------------------------------------------
Map a letter to 0-25, add the shift, wrap with `% 26`, map back:

    encode 'x' with shift 3:
        'x' is letter 23  ->  (23 + 3) % 26 = 0  ->  'a'

    decode is the inverse: subtract the shift.
        'a' with shift 3  ->  (0 - 3) % 26 = 23  ->  'x'

Upper- and lower-case letters are shifted within their own range so case is
preserved. Characters that are not letters (spaces, digits, punctuation) are
left untouched.

Complexity
----------
    Time  : O(n)  — one constant-time shift per character.
    Space : O(n)  — a new string is built for the output.

Standalone reference implementation (Python standard library only). Run it:

    python caesar_cipher.py
"""

from __future__ import annotations

COMPLEXITY = {"time": "O(n)", "space": "O(n)"}


def _shift_char(char: str, shift: int) -> str:
    """Shift a single letter by `shift`, preserving case; leave non-letters as-is."""
    if "a" <= char <= "z":
        base = ord("a")
    elif "A" <= char <= "Z":
        base = ord("A")
    else:
        return char  # not a letter — pass it straight through

    # Position within the alphabet (0-25), shifted and wrapped with mod 26.
    position = (ord(char) - base + shift) % 26
    return chr(base + position)


def caesar_cipher(text: str, shift: int, mode: str = "encode") -> dict:
    """Encode or decode `text` with a Caesar shift.

    `shift` is taken modulo 26, and decoding negates it — so encoding then
    decoding with the same shift returns the original text.

    >>> caesar_cipher("Hello", 3, "encode")["output"]
    'Khoor'
    >>> caesar_cipher("Khoor", 3, "decode")["output"]
    'Hello'
    >>> caesar_cipher("abc xyz", 2, "encode")["output"]   # wraps z->b, spaces kept
    'cde zab'
    """
    # Decoding is just encoding with the opposite shift.
    effective_shift = shift % 26
    if mode == "decode":
        effective_shift = -effective_shift

    output = "".join(_shift_char(char, effective_shift) for char in text)

    return {"output": output, "shift_used": shift % 26, "mode": mode}


def _demo() -> None:
    """Encode a few samples, then decode them back to prove the round-trip."""
    examples = [
        ("Hello", 3),
        ("Attack at dawn", 5),
        ("Veni Vidi Vici", 13),  # shift 13 is ROT13, its own inverse
    ]

    print("Caesar Cipher — shift within the alphabet (mod 26)")
    print("=" * 50)
    for text, shift in examples:
        encoded = caesar_cipher(text, shift, "encode")["output"]
        decoded = caesar_cipher(encoded, shift, "decode")["output"]
        print(f'\nshift {shift:>2}:  "{text}"')
        print(f'           encode -> "{encoded}"')
        print(f'           decode -> "{decoded}"  (matches original: {decoded == text})')


if __name__ == "__main__":
    _demo()
