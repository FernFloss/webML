from __future__ import annotations
import cv2
import numpy as np


def draw_detections(
    frame_bgr: np.ndarray,
    boxes: np.ndarray,
    confs: np.ndarray,
) -> np.ndarray:
    """
    Рисуем прямоугольники и подписи "person: conf".
    """
    annotated = frame_bgr.copy()
    for (x1, y1, x2, y2), conf in zip(boxes, confs):
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"person: {conf:.2f}"
        (tw, th), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        cv2.rectangle(
            annotated,
            (x1, y1 - th - 6),
            (x1 + tw + 4, y1),
            (0, 0, 0),
            -1,
        )
        cv2.putText(
            annotated,
            label,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
    return annotated


def draw_count_badge(frame_bgr: np.ndarray, count: int) -> np.ndarray:
    """
    Рисуем бейджик с общим количеством людей.
    Для веб-сервиса не включаем
    """
    annotated = frame_bgr.copy()
    h = annotated.shape[0]
    label = f"count: {count}"
    (tw, th), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
    )
    x1, y1 = 10, h - 20 - th
    cv2.rectangle(
        annotated,
        (x1 - 6, y1 - th - 6),
        (x1 + tw + 6, y1 + baseline + 6),
        (0, 0, 0),
        -1,
    )
    cv2.putText(
        annotated,
        label,
        (x1, y1),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    return annotated
