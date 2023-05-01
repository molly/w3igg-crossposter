from constants import MARGIN


def calculate_optimal_segments(entry_height, possible_splits, num_segments):
    """Return an array of locations at which to split the image to achieve the target number of segments.

    Args:
        entry_height: Total height of entry in px, multiplied by scaling factor
        possible_splits: Possible y coordinates to split the image. Each element corresponds to a paragraph, starting
            at the second paragraph in the entry.
        num_segments: Number of segments to target in result

    Returns:
        Array of objects containing the y coordinate at which to split the image, and the number of paragraphs included
        in the segment (later used to align alt text with the image segments)
    """
    segments = []
    rough_height = entry_height / num_segments  # Approx height of each segment
    target = rough_height  # Y position of the next target split
    last = 0
    paragraph_count = 0
    for current in possible_splits:
        paragraph_count += 1
        if last < target < current:
            # Choose the split that's closest to the target
            if last != 0 and abs(target - last) < abs(target - current):
                segments.append({"y": last + MARGIN, "paragraphs": paragraph_count})
            else:
                segments.append({"y": current + MARGIN, "paragraphs": paragraph_count})
            if len(segments) == num_segments - 1:
                break
            paragraph_count = 0
            target += rough_height
        last = current
    return segments
