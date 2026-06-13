"""Seed the catalogue: 4 categories, 12 operations, and curated examples.

This data is the reference content the backend and frontend build against
(contract §1, §2, §9). It is **idempotent** — rows are matched by their stable
`slug` and updated in place, so running it repeatedly is safe and never
duplicates. Examples are replaced wholesale per operation on each run.

Run it (from `backend/`, with the virtual environment active and a database
reachable via DATABASE_URL):

    python -m app.database.seed
"""

from __future__ import annotations

import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.base  # noqa: F401  — registers all models on the metadata
from app.database.connection import AsyncSessionLocal
from app.modules.catalogue.models import Category, Operation
from app.modules.examples.models import Example


# ---------------------------------------------------------------------------
# Small builders so each operation's inputSpec reads clearly (contract §2).
# Keys are camelCase because the inputSpec JSONB is stored in the API's shape.
# ---------------------------------------------------------------------------
def string_field(name: str, label: str, max_length: int, **constraints) -> dict:
    field = {
        "name": name,
        "label": label,
        "type": "string",
        "required": True,
        "constraints": {"maxLength": max_length, **constraints},
    }
    return field


def select_field(name: str, label: str, options: list[tuple[str, str]], default: str) -> dict:
    return {
        "name": name,
        "label": label,
        "type": "select",
        "required": True,
        "default": default,
        "constraints": {
            "options": [{"value": value, "label": text} for value, text in options]
        },
    }


def integer_field(name: str, label: str, minimum: int, maximum: int, default: int) -> dict:
    return {
        "name": name,
        "label": label,
        "type": "integer",
        "required": True,
        "default": default,
        "constraints": {"min": minimum, "max": maximum},
    }


_REVERSE_MODES = [
    ("reverse", "Reverse"),
    ("upper", "Upper case"),
    ("lower", "Lower case"),
    ("title", "Title case"),
    ("swapcase", "Swap case"),
]
_CODEC_MODES = [("encode", "Encode"), ("decode", "Decode")]


# ---------------------------------------------------------------------------
# Catalogue content.
# ---------------------------------------------------------------------------
CATEGORIES = [
    {
        "slug": "analysis",
        "name": "Analysis & Properties",
        "description": "Inspect a single string to report its structure and characteristics.",
        "display_order": 1,
    },
    {
        "slug": "search",
        "name": "Search & Matching",
        "description": "Locate a pattern within a text and report where and how often it occurs.",
        "display_order": 2,
    },
    {
        "slug": "comparison",
        "name": "Comparison & Similarity",
        "description": "Measure how two strings relate to one another.",
        "display_order": 3,
    },
    {
        "slug": "transform",
        "name": "Transformation & Encoding",
        "description": "Produce a new string from an input through reversible or rule-based change.",
        "display_order": 4,
    },
]

OPERATIONS = [
    # --- Analysis & Properties -------------------------------------------
    {
        "slug": "palindrome_check",
        "name": "Palindrome Detection",
        "category": "analysis",
        "description": "Check whether a string reads the same forwards and backwards.",
        "explanation": (
            "Two pointers start at the ends and move inward, comparing characters "
            "in pairs; the first mismatch proves it is not a palindrome."
        ),
        "time": "O(n)",
        "space": "O(1)",
        "viz": "result",
        "input_spec": {"fields": [string_field("text", "Text", 200)]},
        "examples": [
            {"label": "Classic palindrome", "inputs": {"text": "racecar"},
             "note": "Reads identically in both directions."},
            {"label": "Not a palindrome", "inputs": {"text": "hello"},
             "note": "Fails at the very first comparison."},
        ],
    },
    {
        "slug": "char_frequency",
        "name": "Character Frequency Analysis",
        "category": "analysis",
        "description": "Count how many times each character appears in a string.",
        "explanation": (
            "A single pass tallies each character in a hash map, then reports the "
            "total length and the number of distinct characters."
        ),
        "time": "O(n)",
        "space": "O(k)",
        "viz": "result",
        "input_spec": {"fields": [string_field("text", "Text", 200)]},
        "examples": [
            {"label": "Repeated letters", "inputs": {"text": "banana"},
             "note": "Shows a clear frequency distribution."},
        ],
    },
    {
        "slug": "longest_palindrome",
        "name": "Longest Palindromic Substring",
        "category": "analysis",
        "description": "Find the longest contiguous substring that is a palindrome.",
        "explanation": (
            "Each position is treated as a possible centre and expanded outward "
            "while the mirror holds, tracking the widest palindrome found."
        ),
        "time": "O(n²)",
        "space": "O(1)",
        "viz": "step_log",
        "input_spec": {"fields": [string_field("text", "Text", 200)]},
        "examples": [
            {"label": "Two valid answers", "inputs": {"text": "babad"},
             "note": "Has two answers of equal length: 'bab' and 'aba'."},
            {"label": "Hidden in the middle", "inputs": {"text": "forgeeksskeegfor"},
             "note": "Contains the palindrome 'geeksskeeg'."},
        ],
    },
    # --- Search & Matching ------------------------------------------------
    {
        "slug": "find_all_occurrences",
        "name": "Find All Occurrences",
        "category": "search",
        "description": "Report every position where a pattern occurs in a text.",
        "explanation": (
            "The pattern is slid across the text one position at a time and "
            "compared; each full match records its start index, including overlaps."
        ),
        "time": "O(n·m)",
        "space": "O(1)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("text", "Text", 200),
            string_field("pattern", "Pattern", 100),
        ]},
        "examples": [
            {"label": "Repeated pattern", "inputs": {"text": "abcabcabc", "pattern": "abc"},
             "note": "Three matches at positions 0, 3 and 6."},
        ],
    },
    {
        "slug": "count_occurrences",
        "name": "Occurrence Counter",
        "category": "search",
        "description": "Count how many times a pattern occurs in a text.",
        "explanation": (
            "Like find-all, but only the running tally is kept rather than every "
            "position; overlapping matches are counted."
        ),
        "time": "O(n)",
        "space": "O(1)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("text", "Text", 200),
            string_field("pattern", "Pattern", 100),
        ]},
        "examples": [
            {"label": "Overlapping matches", "inputs": {"text": "aaaa", "pattern": "aa"},
             "note": "Counts overlaps, giving three occurrences."},
        ],
    },
    {
        "slug": "kmp_search",
        "name": "Knuth-Morris-Pratt Search",
        "category": "search",
        "description": "Find every position where a pattern occurs in a text in linear time.",
        "explanation": (
            "KMP precomputes a failure table from the pattern so that, on a "
            "mismatch, it shifts the pattern by the longest reusable prefix instead "
            "of restarting — behaving like a deterministic finite automaton "
            "scanning the text."
        ),
        "time": "O(n+m)",
        "space": "O(m)",
        "viz": "full",
        "input_spec": {"fields": [
            string_field("text", "Text", 200),
            string_field("pattern", "Pattern", 100),
        ]},
        "examples": [
            {"label": "Failure table fires",
             "inputs": {"text": "ABABDABACDABABCABAB", "pattern": "ABABCABAB"},
             "note": "Forces several non-trivial jumps using the failure function."},
        ],
    },
    # --- Comparison & Similarity -----------------------------------------
    {
        "slug": "anagram_check",
        "name": "Anagram Detection",
        "category": "comparison",
        "description": "Check whether two strings are rearrangements of the same characters.",
        "explanation": (
            "Both strings are reduced to character-frequency maps; they are "
            "anagrams exactly when the two maps are identical."
        ),
        "time": "O(n)",
        "space": "O(k)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("source", "Source", 60),
            string_field("target", "Target", 60),
        ]},
        "examples": [
            {"label": "Classic anagram", "inputs": {"source": "listen", "target": "silent"},
             "note": "Same letters, different order."},
        ],
    },
    {
        "slug": "edit_distance",
        "name": "Levenshtein Edit Distance",
        "category": "comparison",
        "description": "Measure the minimum single-character edits to turn one string into another.",
        "explanation": (
            "A dynamic-programming grid fills cell by cell with the cost of "
            "transforming prefixes; the final cell is the distance and the path "
            "traced back through it reveals the actual edits."
        ),
        "time": "O(n·m)",
        "space": "O(n·m)",
        "viz": "full",
        "input_spec": {"fields": [
            string_field("source", "Source", 60),
            string_field("target", "Target", 60),
        ]},
        "examples": [
            {"label": "Kitten to sitting", "inputs": {"source": "kitten", "target": "sitting"},
             "note": "The textbook example: three edits."},
        ],
    },
    {
        "slug": "lcs",
        "name": "Longest Common Subsequence",
        "category": "comparison",
        "description": "Find the longest subsequence common to two strings.",
        "explanation": (
            "A dynamic-programming grid records the longest common subsequence "
            "length for each pair of prefixes; tracing back rebuilds the subsequence."
        ),
        "time": "O(n·m)",
        "space": "O(n·m)",
        "viz": "step_log",
        "input_spec": {"fields": [
            string_field("source", "Source", 60),
            string_field("target", "Target", 60),
        ]},
        "examples": [
            {"label": "Shared subsequence", "inputs": {"source": "ABCBDAB", "target": "BDCAB"},
             "note": "Longest common subsequence is 'BCAB'."},
        ],
    },
    # --- Transformation & Encoding ---------------------------------------
    {
        "slug": "reverse_transform",
        "name": "Reversal & Case Transform",
        "category": "transform",
        "description": "Transform a string by reversing it or changing its letter case.",
        "explanation": (
            "A mode selects one rewrite — reverse, upper, lower, title, or "
            "swapcase — applied across the whole string."
        ),
        "time": "O(n)",
        "space": "O(n)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("text", "Text", 200),
            select_field("mode", "Mode", _REVERSE_MODES, default="reverse"),
        ]},
        "examples": [
            {"label": "Reverse", "inputs": {"text": "Hello World", "mode": "reverse"},
             "note": "Characters in the opposite order."},
        ],
    },
    {
        "slug": "caesar_cipher",
        "name": "Caesar Cipher",
        "category": "transform",
        "description": "Encode or decode text with a Caesar shift cipher.",
        "explanation": (
            "Each letter is shifted a fixed number of places along the alphabet "
            "using modular arithmetic; decoding shifts the other way."
        ),
        "time": "O(n)",
        "space": "O(n)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("text", "Text", 200, allowedAlphabet="A-Za-z "),
            integer_field("shift", "Shift", minimum=0, maximum=25, default=3),
            select_field("mode", "Mode", _CODEC_MODES, default="encode"),
        ]},
        "examples": [
            {"label": "Shift by three", "inputs": {"text": "Hello", "shift": 3, "mode": "encode"},
             "note": "Julius Caesar's own shift of three."},
        ],
    },
    {
        "slug": "run_length",
        "name": "Run-Length Encoding",
        "category": "transform",
        "description": "Compress or expand text using run-length encoding.",
        "explanation": (
            "Runs of identical characters are replaced by the character followed "
            "by its count when encoding; decoding reverses the process."
        ),
        "time": "O(n)",
        "space": "O(n)",
        "viz": "result",
        "input_spec": {"fields": [
            string_field("text", "Text", 200),
            select_field("mode", "Mode", _CODEC_MODES, default="encode"),
        ]},
        "examples": [
            {"label": "Compress repeats", "inputs": {"text": "aaabbc", "mode": "encode"},
             "note": "Encodes to 'a3b2c1'."},
        ],
    },
]


async def _upsert_category(db: AsyncSession, data: dict) -> Category:
    existing = (
        await db.execute(select(Category).where(Category.slug == data["slug"]))
    ).scalar_one_or_none()
    if existing is None:
        existing = Category(slug=data["slug"])
        db.add(existing)
    existing.name = data["name"]
    existing.description = data["description"]
    existing.display_order = data["display_order"]
    await db.flush()
    return existing


async def _upsert_operation(db: AsyncSession, data: dict, category_id: int) -> Operation:
    existing = (
        await db.execute(select(Operation).where(Operation.slug == data["slug"]))
    ).scalar_one_or_none()
    if existing is None:
        existing = Operation(slug=data["slug"])
        db.add(existing)
    existing.name = data["name"]
    existing.category_id = category_id
    existing.description = data["description"]
    existing.explanation = data["explanation"]
    existing.input_spec = data["input_spec"]
    existing.time_complexity = data["time"]
    existing.space_complexity = data["space"]
    existing.visualisation_level = data["viz"]
    await db.flush()
    return existing


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        categories_by_slug: dict[str, Category] = {}
        for category_data in CATEGORIES:
            category = await _upsert_category(db, category_data)
            categories_by_slug[category.slug] = category

        for op_data in OPERATIONS:
            category = categories_by_slug[op_data["category"]]
            operation = await _upsert_operation(db, op_data, category.category_id)

            # Replace this operation's examples wholesale so the seed stays the
            # single source of truth (and re-runs don't accumulate duplicates).
            await db.execute(
                delete(Example).where(Example.operation_id == operation.operation_id)
            )
            for order, example in enumerate(op_data["examples"]):
                db.add(
                    Example(
                        operation_id=operation.operation_id,
                        label=example["label"],
                        inputs=example["inputs"],
                        note=example["note"],
                        display_order=order,
                    )
                )

        await db.commit()

    print(
        f"Seed complete: {len(CATEGORIES)} categories, {len(OPERATIONS)} operations, "
        f"{sum(len(o['examples']) for o in OPERATIONS)} examples."
    )


if __name__ == "__main__":
    asyncio.run(seed())
