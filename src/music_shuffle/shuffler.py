import random


def generate_unique_numbers(
    count: int,
    minimum: int,
    maximum: int,
    rng: random.Random | None = None,
) -> list[int]:
    """Generate unique random integers from an inclusive range."""
    if minimum > maximum:
        raise ValueError("Minimum number must not exceed maximum number.")

    available = maximum - minimum + 1
    if count > available:
        raise ValueError(
            f"Range contains only {available} unique numbers, "
            f"but {count} files need numbers."
        )

    rng = rng or random.Random()
    return rng.sample(range(minimum, maximum + 1), count)
