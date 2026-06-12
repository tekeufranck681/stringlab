def longest_palindromic_substring(text: str):

    if not text:
        return {
            "substring": "",
            "length": 0,
            "trace": []
        }

    start = 0
    max_length = 1

    trace = []

    def expand(left, right):

        nonlocal start
        nonlocal max_length

        while (
            left >= 0
            and right < len(text)
            and text[left] == text[right]
        ):

            current = text[left:right + 1]

            trace.append(
                {
                    "left": left,
                    "right": right,
                    "substring": current
                }
            )

            if len(current) > max_length:
                start = left
                max_length = len(current)

            left -= 1
            right += 1

    for i in range(len(text)):

        expand(i, i)

        expand(i, i + 1)

    return {
        "substring": text[start:start + max_length],
        "length": max_length,
        "trace": trace,
        "complexity": {
            "time": "O(n²)",
            "space": "O(1)"
        }
    }