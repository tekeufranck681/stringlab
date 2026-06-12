from collections import Counter


def analyze_frequency(text: str):

    counter = Counter(text)

    frequencies = []

    for char, count in sorted(
        counter.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        frequencies.append(
            {
                "character": char,
                "count": count
            }
        )

    return {
        "total_characters": len(text),
        "unique_characters": len(counter),
        "frequencies": frequencies
    }