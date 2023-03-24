from utils.constants import Align
from typing import Tuple
import pygame

def align(x: int, y: int, width: int, height: int, anchor: Align) -> Tuple[int, int]:
    return x - width / 2  * anchor.value[1], y - height / 2 * anchor.value[0]

def scale(img: pygame.Surface, factor: float) -> pygame.Surface:
    w, h = img.get_width() * factor, img.get_height() * factor
    return pygame.transform.scale(img, (int(w), int(h)))