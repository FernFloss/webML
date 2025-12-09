from __future__ import annotations
from pathlib import Path
from typing import Iterator, Tuple
import cv2
import numpy as np


def iter_images(folder: Path) -> Iterator[Tuple[Path, np.ndarray]]:

    exts = {".jpg", ".jpeg", ".png", ".bmp"}
    if not folder.exists():
        raise FileNotFoundError(folder)

    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in exts:
            img = cv2.imread(str(p))
            if img is not None:
                yield p, img


def save_image(img: np.ndarray, out_path: Path) -> None:

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(out_path), img):
        raise RuntimeError(f"сannot save {out_path}")
