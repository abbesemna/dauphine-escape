import pygame
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

def _scale_pixel(surf, size):
    """Scale surface for pixel art (no smoothscale)."""
    return pygame.transform.scale(surf, (size, size))


def _load_mp4_frames(mp4_path, out_list):
    """Load all frames from one .mp4 into out_list as pygame Surfaces (needs cv2)."""
    if not _CV2_AVAILABLE:
        return
    try:
        cap = cv2.VideoCapture(str(mp4_path))
        if not cap.isOpened():
            return
        import numpy as np
        while True:
            ret, bgr = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            rgb_cont = np.ascontiguousarray(rgb)
            surf = pygame.image.frombuffer(rgb_cont.tobytes(), (w, h), 'RGB')
            surf = pygame.transform.scale(surf, (WINDOW_WIDTH, WINDOW_HEIGHT))
            out_list.append(surf)
        cap.release()
    except Exception:
        pass
