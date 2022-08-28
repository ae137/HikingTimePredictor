import pytest

from utils import get_pseudo_probability_for_path


def test_pseudo_probability_reproducible() -> None:
    scores = [get_pseudo_probability_for_path("test_string.txt") for i in range(10)]

    assert all(score == scores[0] for score in scores)


def test_pseudo_probability_different() -> None:
    score_1 = get_pseudo_probability_for_path("test_string.txt")
    score_2 = get_pseudo_probability_for_path("test_string_.txt")

    assert not score_1 == pytest.approx(score_2)
