import pyautogui
from config import SCROLL_SENSITIVITY
import numpy as np
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, CAM_WIDTH, CAM_HEIGHT,
                    SCROLL_SENSITIVITY, MOUSE_SMOOTHING, PINCH_CLICK_THRESHOLD, MOUSE_DEAD_ZONE)

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0


class MouseController:
    def __init__(self):
        self.prev_x = SCREEN_WIDTH  // 2
        self.prev_y = SCREEN_HEIGHT // 2

        self.dragging      = False
        self.was_clicking  = False
        self.scroll_prev_y = None

    # ─────────────────────────── Mouse movement ───────────────────────────

    def move(self, index_tip):
        """Move mouse based on index fingertip position"""
        if index_tip is None:
            return

        ix, iy = index_tip

        # Map camera coords → screen coords
        # Use wider margins so full screen is reachable
        tx = int(np.interp(ix, [0, CAM_WIDTH],  [0, SCREEN_WIDTH]))
        ty = int(np.interp(iy, [0, CAM_HEIGHT], [0, SCREEN_HEIGHT]))

        # Dead zone — ignore micro-movements
        if (abs(tx - self.prev_x) < MOUSE_DEAD_ZONE and
                abs(ty - self.prev_y) < MOUSE_DEAD_ZONE):
            return

        # Smooth interpolation
        sx = self.prev_x + (tx - self.prev_x) / MOUSE_SMOOTHING
        sy = self.prev_y + (ty - self.prev_y) / MOUSE_SMOOTHING

        sx = max(0, min(SCREEN_WIDTH  - 1, sx))
        sy = max(0, min(SCREEN_HEIGHT - 1, sy))

        pyautogui.moveTo(int(sx), int(sy))
        self.prev_x = sx
        self.prev_y = sy

    # ─────────────────────────── Click ───────────────────────────

    def handle_pinch(self, pinch_dist):
        """Left click on pinch gesture"""
        if pinch_dist is None:
            self.was_clicking = False
            return

        is_pinching = pinch_dist < PINCH_CLICK_THRESHOLD

        if is_pinching and not self.was_clicking:
            pyautogui.click()

        self.was_clicking = is_pinching

    def right_click(self):
        pyautogui.rightClick()

    # ─────────────────────────── Drag ───────────────────────────

    def start_drag(self):
        if not self.dragging:
            pyautogui.mouseDown()
            self.dragging = True

    def stop_drag(self):
        if self.dragging:
            pyautogui.mouseUp()
            self.dragging = False

    # ─────────────────────────── Scroll ───────────────────────────

    def scroll(self, index_tip):
        """Scroll based on vertical finger movement"""
        if index_tip is None:
            self.scroll_prev_y = None
            return

        _, iy = index_tip

        if self.scroll_prev_y is not None:
            delta = self.scroll_prev_y - iy
            if abs(delta) > 5:
                pyautogui.scroll(int(delta / SCROLL_SENSITIVITY))

        self.scroll_prev_y = iy

    def reset_scroll(self):
        self.scroll_prev_y = None