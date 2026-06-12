def check_palindrome(text: str):

    text = text.strip()

    left = 0
    right = len(text) - 1

    trace = []

    while left < right:

        match = text[left] == text[right]

        trace.append({
            "left_index": left,
            "right_index": right,
            "left_char": text[left],
            "right_char": text[right],
            "match": match
        })

        if not match:

            return {
                "operation": "Palindrome Detection",
                "result": False,
                "explanation": (
                    f"Mismatch between '{text[left]}' "
                    f"and '{text[right]}'."
                ),
                "complexity": {
                    "time": "O(n)",
                    "space": "O(1)"
                },
                "trace": trace
            }

        left += 1
        right -= 1

    return {
        "operation": "Palindrome Detection",
        "result": True,
        "explanation":
            "The string reads the same forwards and backwards.",
        "complexity": {
            "time": "O(n)",
            "space": "O(1)"
        },
        "trace": trace
    }