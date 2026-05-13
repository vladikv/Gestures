import cv2
import numpy as np


class Overlay:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

        # Notification system
        self.notification      = ''
        self.notification_life = 0

    # ─────────────────────────── Main draw ───────────────────────────

    def draw(self, frame, gesture, mode, media):
        self._draw_top_bar(frame, gesture, mode)
        self._draw_volume_bar(frame, media)
        self._draw_gesture_guide(frame)
        self._draw_notification(frame)
        return frame

    # ─────────────────────────── Top bar ───────────────────────────

    def _draw_top_bar(self, frame, gesture, mode):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, 60), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        # App title
        cv2.putText(frame, 'GestureOS', (14, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 220, 220), 2)

        # Active gesture
        gesture_color = (0, 255, 100) if gesture != 'unknown' else (120, 120, 120)
        cv2.putText(frame, f'Gesture: {gesture}', (200, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, gesture_color, 1)

        # Mode
        cv2.putText(frame, f'Mode: {mode}', (520, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    # ─────────────────────────── Volume bar ───────────────────────────

    def _draw_volume_bar(self, frame, media):
        vol = media.get_volume() if media else None
        if vol is None:
            return

        bar_x, bar_y = self.width - 40, 80
        bar_h = 200
        filled = int(bar_h * vol)

        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + 20, bar_y + bar_h),
                      (50, 50, 50), -1)
        # Fill
        color = (0, 200, 255) if vol > 0.7 else (0, 255, 150)
        cv2.rectangle(frame,
                      (bar_x, bar_y + bar_h - filled),
                      (bar_x + 20, bar_y + bar_h),
                      color, -1)
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + 20, bar_y + bar_h),
                      (180, 180, 180), 1)
        # Label
        cv2.putText(frame, f'{int(vol * 100)}%', (bar_x - 5, bar_y + bar_h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(frame, 'VOL', (bar_x, bar_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    # ─────────────────────────── Gesture guide ───────────────────────────

    def _draw_gesture_guide(self, frame):
        h = self.height
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 36), (self.width, h), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        hints = ('☞ Index=mouse   ✊ Fist=drag/pause   ✋ Palm=desktop/swipe   '
                 '👍 Thumb=vol+   🤙 Pinky=vol-   ☞☞☞ 3-fin=next   '
                 'Q=quit  S=screenshot')
        cv2.putText(frame, hints, (10, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 160, 160), 1)

    # ─────────────────────────── Notification ───────────────────────────

    def notify(self, text, duration=45):
        """Show a temporary notification on screen"""
        self.notification      = text
        self.notification_life = duration

    def _draw_notification(self, frame):
        if self.notification_life <= 0:
            return

        alpha = min(1.0, self.notification_life / 15)
        color = (int(0 * alpha), int(255 * alpha), int(200 * alpha))

        cv2.putText(frame, self.notification,
                    (self.width // 2 - 200, self.height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        self.notification_life -= 1

    # ─────────────────────────── FPS ───────────────────────────

    def draw_fps(self, frame, fps):
        cv2.putText(frame, f'FPS {int(fps)}', (14, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 255, 80), 1)