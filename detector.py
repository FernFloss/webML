from __future__ import annotations
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import torch
try:
    torch.backends.mkldnn.enabled = False
except Exception:
    pass

import cv2
import numpy as np
from ml_people_counter import PeopleCounter


class PeopleCounterService:
    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        device: str = "auto",
        conf_thres: float = 0.30,
        iou_thres: float = 0.60,
        imgsz: int = 960,
    ) -> None:

        self.counter = PeopleCounter(
            model_path=model_path,
            device=device,
            conf_thres=conf_thres,
            iou_thres=iou_thres,
            imgsz=imgsz,
        )

    def count_people_from_bytes(self, image_bytes: bytes) -> int:

        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise RuntimeError("failed to decode image from bytes")

        annotated, count, boxes, confs = self.counter.process_frame(frame_bgr)

        return count


people_counter_service: Optional[PeopleCounterService] = None


def get_people_counter_service() -> PeopleCounterService:
    global people_counter_service
    if people_counter_service is None:
        people_counter_service = PeopleCounterService()
    return people_counter_service


def count_people_on_frame(image_bytes: bytes) -> int:
    svc = get_people_counter_service()
    return svc.count_people_from_bytes(image_bytes)
