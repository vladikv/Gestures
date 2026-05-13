import cv2
import numpy as np
import pyautogui


class AirKeyboard:
    """
    Virtual keyboard rendered on camera frame.
    Index fingertip hovers over keys — pinch to press.
    Types into whatever field is currently active on the OS.
    """

    # Keyboard layout rows
    ROWS = [
        ['Q','W','E','R','T','Y','U','I','O','P'],
        ['A','S','D','F','G','H','J','K','L'],
        ['Z','X','C','V','B','N','M','←','SPACE'],
    ]

    KEY_W      = 62   # key width  (px)
    KEY_H      = 58   # key height (px)
    KEY_GAP    = 6    # gap between keys
    START_X    = 30   # left margin
    START_Y    = 320  # top of keyboard on frame

    PINCH_THRESHOLD  = 38   # px — pinch distance to trigger press
    COOLDOWN_FRAMES  = 18   # frames between key presses
    HOVER_FRAMES     = 6    # frames finger must hover before highlight locks

    def __init__(self):
        self.cooldown      = 0
        self.hovered_key   = None
        self.hover_counter = 0
        self.last_pressed  = ''
        self.typed_text    = ''   # local display buffer

        # Pre-compute key rectangles: {label: (x1,y1,x2,y2)}
        self.key_rects = self._build_rects()

    # ─────────────────────────── Layout ───────────────────────────

    def _build_rects(self):
        rects = {}
        step  = self.KEY_W + self.KEY_GAP

        for row_i, row in enumerate(self.ROWS):
            # Centre each row
            row_w  = len(row) * step - self.KEY_GAP
            offset = (10 * step - row_w) // 2
            y1     = self.START_Y + row_i * (self.KEY_H + self.KEY_GAP)
            y2     = y1 + self.KEY_H

            for col_i, label in enumerate(row):
                x1 = self.START_X + offset + col_i * step
                # SPACE key is wider
                w  = self.KEY_W * 3 if label == 'SPACE' else self.KEY_W
                x2 = x1 + w
                rects[label] = (x1, y1, x2, y2)

        return rects

    # ─────────────────────────── Update ───────────────────────────

    def update(self, index_tip, pinch_dist):
        """
        Call every frame.
        index_tip  — (x, y) of index fingertip or None
        pinch_dist — float distance thumb↔index or None
        Returns pressed key label or None.
        """
        if self.cooldown > 0:
            self.cooldown -= 1

        if index_tip is None:
            self.hovered_key   = None
            self.hover_counter = 0
            return None

        # Find which key the finger is over
        found = None
        for label, (x1, y1, x2, y2) in self.key_rects.items():
            if x1 <= index_tip[0] <= x2 and y1 <= index_tip[1] <= y2:
                found = label
                break

        # Hover stability
        if found == self.hovered_key:
            self.hover_counter = min(self.hover_counter + 1, self.HOVER_FRAMES)
        else:
            self.hovered_key   = found
            self.hover_counter = 0

        # Pinch = press
        is_pinching = pinch_dist is not None and pinch_dist < self.PINCH_THRESHOLD
        if (is_pinching
                and self.hovered_key is not None
                and self.hover_counter >= self.HOVER_FRAMES
                and self.cooldown == 0):
            self._press(self.hovered_key)
            self.cooldown = self.COOLDOWN_FRAMES
            return self.hovered_key

        return None

    def _press(self, label):
        if label == '←':
            pyautogui.press('backspace')
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        elif label == 'SPACE':
            pyautogui.press('space')
            self.typed_text += ' '
        else:
            pyautogui.press(label.lower())
            self.typed_text += label
        self.last_pressed = label

    # ─────────────────────────── Render ───────────────────────────

    def draw(self, frame, index_tip, pinch_dist):
        """Draw keyboard overlay onto frame"""
        is_pinching = pinch_dist is not None and pinch_dist < self.PINCH_THRESHOLD

        for label, (x1, y1, x2, y2) in self.key_rects.items():
            is_hovered = (label == self.hovered_key
                          and self.hover_counter >= self.HOVER_FRAMES)
            is_active  = (is_hovered and is_pinching and self.cooldown == 0)

            self._draw_key(frame, label, x1, y1, x2, y2, is_hovered, is_active)

        # Typed text display bar
        self._draw_text_bar(frame)

        # Finger dot
        if index_tip:
            cv2.circle(frame, index_tip, 8,  (0, 255, 255), -1)
            cv2.circle(frame, index_tip, 10, (255, 255, 255), 1)

        return frame

    def _draw_key(self, frame, label, x1, y1, x2, y2,
                  is_hovered, is_active):
        overlay = frame.copy()

        # Fill color
        if is_active:
            fill = (0, 220, 0)
        elif is_hovered:
            fill = (60, 60, 180)
        else:
            fill = (30, 30, 30)

        cv2.rectangle(overlay, (x1, y1), (x2, y2), fill, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Border
        border = (0, 255, 200) if is_hovered else (100, 100, 100)
        cv2.rectangle(frame, (x1, y1), (x2, y2), border, 1)

        # Label text
        font_scale = 0.38 if label == 'SPACE' else 0.55
        text_color = (255, 255, 255)
        tw, th = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
                                 font_scale, 1)[0]
        tx = x1 + ((x2 - x1) - tw) // 2
        ty = y1 + ((y2 - y1) + th) // 2
        cv2.putText(frame, label, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 1)

        # Hover progress bar at bottom of key
        if is_hovered and not is_active:
            progress = self.hover_counter / self.HOVER_FRAMES
            bar_w    = int((x2 - x1) * progress)
            cv2.rectangle(frame, (x1, y2 - 3), (x1 + bar_w, y2),
                          (0, 200, 255), -1)

    def _draw_text_bar(self, frame):
        h = frame.shape[0]
        bar_y = self.START_Y - 48

        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.START_X, bar_y),
                      (frame.shape[1] - self.START_X, bar_y + 40),
                      (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        # Border
        cv2.rectangle(frame,
                      (self.START_X, bar_y),
                      (frame.shape[1] - self.START_X, bar_y + 40),
                      (80, 80, 80), 1)

        # Text — show last 55 chars so it fits
        display = self.typed_text[-55:] if len(self.typed_text) > 55 else self.typed_text
        cv2.putText(frame, display + '|', (self.START_X + 8, bar_y + 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 200), 1)

    # ─────────────────────────── Helpers ───────────────────────────

    def clear_text(self):
        self.typed_text = ''

    def get_typed(self):
        return self.typed_text