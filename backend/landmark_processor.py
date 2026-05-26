"""
Landmark Processor for ISL SignSpeak

Converts interleaved MediaPipe landmark data from the browser into the
grouped feature format expected by the sklearn RandomForestClassifier models.

Input format  (interleaved, 132 floats):
    [x0, y0, z0, v0,  x1, y1, z1, v1,  ...,  x32, y32, z32, v32]

Output format (interleaved, 132 floats → shape (1, 132)):
    [x0, y0, z0, v0,  x1, y1, z1, v1,  ...,  x32, y32, z32, v32]
"""

import numpy as np

EXPECTED_LENGTH = 132
NUM_LANDMARKS = 33  # 21 hand + 12 pose landmarks (or 33 total)
COMPONENTS_PER_LANDMARK = 4  # x, y, z, visibility


def process_landmarks(landmarks_list: list[float]) -> np.ndarray:
    """
    Pass through interleaved landmark data for the
    trained sklearn models.

    Parameters
    ----------
    landmarks_list : list[float]
        Flat list of 132 floats in interleaved order:
        [x0, y0, z0, v0, x1, y1, z1, v1, ...]

    Returns
    -------
    np.ndarray
        Array of shape (1, 132) in interleaved order:
        [x0, y0, z0, v0, x1, y1, z1, v1, ...]

    Raises
    ------
    ValueError
        If the input length is not exactly 132.
    TypeError
        If the input contains non-numeric values.
    """
    if not isinstance(landmarks_list, (list, tuple)):
        raise TypeError(f"Expected list or tuple, got {type(landmarks_list).__name__}")

    if len(landmarks_list) != EXPECTED_LENGTH:
        raise ValueError(
            f"Expected {EXPECTED_LENGTH} landmark values, got {len(landmarks_list)}"
        )

    try:
        arr = np.array(landmarks_list, dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise TypeError(f"Landmark data contains non-numeric values: {exc}") from exc

    # The CSV files used for training had grouped column names (x_0, x_1...)
    # but the actual data written to them was interleaved.
    # Therefore, the model was trained on interleaved data.
    return arr.reshape(1, EXPECTED_LENGTH)
