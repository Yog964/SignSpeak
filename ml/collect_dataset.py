"""
ISL SignSpeak dataset collection script.

Captures MediaPipe Pose landmarks from a webcam and saves them as a CSV file
with 132 landmark feature columns plus an `action` label column.

Example:
    python collect_dataset.py --action hello --output ../database/Structured/GeneralAction/hello.csv --duration 8
"""

import argparse
import csv
import os
import time
from pathlib import Path

import cv2
import mediapipe as mp


FEATURE_HEADER = [
    f"{dimension}_{index}"
    for dimension in ("x", "y", "z", "visibility")
    for index in range(33)
]


def save_landmarks_to_csv(filename: Path, rows: list[list[float | str]]) -> None:
    """Save collected landmark rows to a CSV file."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    with filename.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(FEATURE_HEADER + ["action"])
        writer.writerows(rows)

    print(f"[OK] Saved {len(rows)} samples to {filename.resolve()}")


def open_camera(camera_indices: list[int]) -> cv2.VideoCapture:
    """Open the first available camera from the provided index list."""
    for index in camera_indices:
        print(f"[INFO] Trying webcam index {index}...")
        camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if camera.isOpened():
            ok, _ = camera.read()
            if ok:
                print(f"[OK] Webcam opened at index {index}")
                return camera
        camera.release()

    for index in camera_indices:
        print(f"[INFO] Trying default backend for webcam index {index}...")
        camera = cv2.VideoCapture(index)
        if camera.isOpened():
            ok, _ = camera.read()
            if ok:
                print(f"[OK] Webcam opened at index {index}")
                return camera
        camera.release()

    raise RuntimeError("Could not open a webcam. Check camera permissions and close other camera apps.")


def collect_dataset(
    action: str,
    output: Path,
    duration: int,
    countdown: int,
    preview_only: bool,
    camera_indices: list[int],
) -> None:
    """Collect one labeled dataset CSV from webcam pose landmarks."""
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    landmark_rows: list[list[float | str]] = []
    recording = False
    counting_down = False
    start_time: float | None = None
    countdown_start: float | None = None

    camera = open_camera(camera_indices)
    window_name = "ISL SignSpeak Dataset Collection"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    print(f"[INFO] Action: {action}")
    print(f"[INFO] Output: {output.resolve()}")
    print(f"[INFO] Mode: {'preview' if preview_only else 'collect'}")
    print("[INFO] Press 's' to start recording, or 'q' to quit.")

    try:
        with mp_pose.Pose() as pose:
            while camera.isOpened():
                ok, frame = camera.read()
                if not ok:
                    print("[ERR] Could not read frame from webcam.")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                    )

                    if recording:
                        landmarks: list[float | str] = []
                        for landmark in results.pose_landmarks.landmark:
                            landmarks.extend(
                                [
                                    landmark.x,
                                    landmark.y,
                                    landmark.z,
                                    landmark.visibility,
                                ]
                            )
                        landmarks.append(action)
                        landmark_rows.append(landmarks)

                        if start_time is not None and time.time() - start_time >= duration:
                            print(f"[INFO] Recording complete for '{action}'.")
                            save_landmarks_to_csv(output, landmark_rows)
                            recording = False
                            landmark_rows = []

                if counting_down and countdown_start is not None:
                    remaining = countdown - int(time.time() - countdown_start)
                    if remaining > 0:
                        cv2.putText(
                            frame,
                            f"GET READY: {remaining}",
                            (120, 240),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (0, 255, 255),
                            5,
                        )
                    else:
                        counting_down = False
                        recording = True
                        start_time = time.time()
                        print(f"[INFO] Started recording '{action}'")
                elif recording and start_time is not None:
                    remaining = max(0, duration - int(time.time() - start_time))
                    cv2.putText(
                        frame,
                        f"RECORDING: {action} ({remaining}s)",
                        (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                else:
                    label = "Preview mode" if preview_only else f"Ready: {action}"
                    cv2.putText(
                        frame,
                        label,
                        (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2,
                    )

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("s") and not recording and not counting_down:
                    if preview_only:
                        print("[INFO] Preview mode is enabled. Re-run without --preview-only to record.")
                    else:
                        counting_down = True
                        countdown_start = time.time()
                        print(f"[INFO] Starting {countdown}s countdown for '{action}'...")
    finally:
        camera.release()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect ISL landmark CSV data from a webcam.")
    parser.add_argument("--action", required=True, help="Label/sign name to store in the action column.")
    parser.add_argument(
        "--output",
        required=True,
        help="CSV output path, for example ../database/Structured/GeneralAction/hello.csv",
    )
    parser.add_argument("--duration", type=int, default=8, help="Recording duration in seconds.")
    parser.add_argument("--countdown", type=int, default=3, help="Countdown before recording starts.")
    parser.add_argument(
        "--camera-indices",
        default="0,1,2",
        help="Comma-separated webcam indices to try, default: 0,1,2.",
    )
    parser.add_argument("--preview-only", action="store_true", help="Open camera without saving data.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    indices = [int(index.strip()) for index in args.camera_indices.split(",") if index.strip()]
    collect_dataset(
        action=args.action,
        output=Path(args.output),
        duration=args.duration,
        countdown=args.countdown,
        preview_only=args.preview_only,
        camera_indices=indices,
    )
