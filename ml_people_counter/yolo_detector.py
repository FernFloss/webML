from __future__ import annotations
from typing import Tuple
import numpy as np
from ultralytics import YOLO


def _resolve_device(device: str | None) -> str:
    dev = (device or "cpu").strip().lower()
    if dev == "auto":
        try:
            import torch

            return "0" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"
    return dev


class YOLOPersonDetector:

    def __init__(
        self,
        model_path: str,
        device: str,
        conf_thres: float,
        iou_thres: float,
        imgsz: int,
    ) -> None:
        self.model = YOLO(model_path)
        self.device = _resolve_device(device)
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.imgsz = imgsz

        self.model.fuse()

    def detect(self, frame_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:

        results = self.model.predict(
            frame_bgr,
            device=self.device,
            conf=self.conf_thres,
            iou=self.iou_thres,
            imgsz=self.imgsz,
            verbose=False,
        )
        r = results[0]
        if not r.boxes or len(r.boxes) == 0:
            return np.zeros((0, 4)), np.zeros((0,))

        xyxy = r.boxes.xyxy.cpu().numpy()
        conf = r.boxes.conf.cpu().numpy()
        cls = r.boxes.cls.cpu().numpy().astype(int)

        mask = cls == 0
        return xyxy[mask], conf[mask]
