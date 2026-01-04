from typing import List, Tuple

def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    if len(numbers) < 2:
        raise ValueError("List must contain at least two numbers")

    closest_pair = (numbers[0], numbers[1])
    min_distance = abs(numbers[1] - numbers[0])

    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            distance = abs(numbers[j] - numbers[i])
            if distance < min_distance:
                min_distance = distance
                closest_pair = (min(numbers[i], numbers[j]), max(numbers[i], numbers[j]))

    return closest_pair