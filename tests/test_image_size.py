from image_size import *


def test_calculate_splits_for_two_segment_post():
    possible_splits = [100, 200, 340, 450, 500, 600]
    splits = calculate_optimal_segments(700, possible_splits, 2)
    assert len(splits) == 1
    assert splits == [340]


def test_calculate_splits_for_three_segment_post():
    possible_splits = [100, 200, 300, 400, 500, 600]
    splits = calculate_optimal_segments(700, possible_splits, 3)
    assert len(splits) == 2
    assert splits == [200, 500]


def test_calculate_splits_for_wonky_post():
    # This is tall enough that it should get three segments, but there aren't enough options for places to split
    possible_splits = [3000]
    splits = calculate_optimal_segments(3200, possible_splits, 3)
    assert len(splits) == 1
    assert splits == [3000]


def test_calculate_splits_with_no_split_options():
    splits = calculate_optimal_segments(900, [], 2)
    assert splits == []
