from image_size import *
from constants import MARGIN


def test_calculate_splits_for_two_segment_post():
    possible_splits = [100, 200, 340, 450, 500, 600]
    splits = calculate_optimal_segments(700, possible_splits, 2)
    assert len(splits) == 1
    assert splits[0]["y"] == 340 + MARGIN
    assert splits[0]["paragraphs"] == 4


def test_calculate_splits_for_three_segment_post():
    possible_splits = [100, 200, 300, 400, 500, 600]
    splits = calculate_optimal_segments(700, possible_splits, 3)
    assert len(splits) == 2
    assert splits[0]["y"] == 200 + MARGIN
    assert splits[0]["paragraphs"] == 3
    assert splits[1]["y"] == 500 + MARGIN
    assert splits[1]["paragraphs"] == 2


def test_calculate_splits_for_wonky_post():
    # This is tall enough that it should get three segments, but there aren't enough options for places to split
    possible_splits = [3000]
    splits = calculate_optimal_segments(3200, possible_splits, 3)
    assert len(splits) == 1
    assert splits[0]["y"] == 3000 + MARGIN
    assert splits[0]["paragraphs"] == 1


def test_calculate_splits_with_no_split_options():
    splits = calculate_optimal_segments(900, [], 2)
    assert splits == []
