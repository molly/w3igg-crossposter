def calculate_optimal_segments(entry_height, possible_splits, num_segments):
    """Return an array of y coordinates at which to split the image to achieve the target number of segments."""
    segments = []
    rough_height = entry_height / num_segments  # Approx height of each segment
    target = rough_height  # Y position of the next target split
    last = 0
    for current in possible_splits:
        if last < target < current:
            # Choose the split that's closest to the target
            if last != 0 and abs(target - last) < abs(target - current):
                segments.append(last)
            else:
                segments.append(current)
            if len(segments) == num_segments - 1:
                break
            target += rough_height
        last = current
    return segments
