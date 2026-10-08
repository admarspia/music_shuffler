import random

import pytest

from music_shuffle.shuffler import generate_unique_numbers


def test_numbers_are_unique():
    numbers = generate_unique_numbers(100, 1, 1000, random.Random(1))
    assert len(numbers) == 100
    assert len(set(numbers)) == 100


def test_range_is_inclusive():
    numbers = generate_unique_numbers(2, 1, 2, random.Random(1))
    assert sorted(numbers) == [1, 2]


def test_too_many_files():
    with pytest.raises(ValueError):
        generate_unique_numbers(3, 1, 2)
