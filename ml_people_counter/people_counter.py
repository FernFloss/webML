from __future__ import annotations
from typing import Tuple
import numpy as np
from .yolo_detector import YOLOPersonDetector
from .overlay import draw_detections


class PeopleCounter:

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        device: str = "auto",
        conf_thres: float = 0.30,
        iou_thres: float = 0.60,
        imgsz: int = 960,
    ) -> None:
        self.detector = YOLOPersonDetector(
            model_path=model_path,
            device=device,
            conf_thres=conf_thres,
            iou_thres=iou_thres,
            imgsz=imgsz,
        )

    def process_frame(
        self, frame_bgr: np.ndarray
    ) -> Tuple[np.ndarray, int, np.ndarray, np.ndarray]:

        boxes, confs = self.detector.detect(frame_bgr)
        annotated = draw_detections(frame_bgr, boxes, confs)
        count = len(boxes)
        return annotated, count, boxes, confs
