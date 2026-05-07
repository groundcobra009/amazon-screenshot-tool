import numpy as np
from PIL import Image
from pathlib import Path


def images_are_same(image_path1: Path, image_path2: Path, threshold: float = 0.001) -> bool:
    """2つの画像を比較し、ほぼ同じならTrueを返す

    threshold: 異なるピクセルの割合がこの値以下なら「同じ」と判定
    """
    img1 = np.array(Image.open(image_path1))
    img2 = np.array(Image.open(image_path2))

    if img1.shape != img2.shape:
        return False

    diff = np.abs(img1.astype(int) - img2.astype(int))
    # 各ピクセルのRGB差分の合計が一定以上なら「異なるピクセル」とカウント
    changed_pixels = np.sum(diff.sum(axis=-1) > 10)
    total_pixels = img1.shape[0] * img1.shape[1]
    change_ratio = changed_pixels / total_pixels

    return change_ratio <= threshold
