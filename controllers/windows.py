import keyboard
import pyautogui
import time
from config import SWIPE_THRESHOLD, SWIPE_COOLDOWN, SHORTCUT_MAP


class WindowsController:
    def __init__(self):
        self.swipe_start_x  = None
        self.cooldown       = 0
        self.fist_start_y   = None
        self.fist_frames    = 0

    # ─────────────────────────── Swipe ───────────────────────────

    def handle_swipe(self, palm_tip):
        """
        Detect horizontal swipe with open palm:
        - swipe right → next virtual desktop
        - swipe left  → previous virtual desktop
        """
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        if palm_tip is None:
            self.swipe_start_x = None
            return None

        x, _ = palm_tip

        if self.swipe_start_x is None:
            self.swipe_start_x = x
            return None

        delta = x - self.swipe_start_x

        if delta > SWIPE_THRESHOLD:
            self._fire('prev_desk')
            self.swipe_start_x = x
            self.cooldown = SWIPE_COOLDOWN
            return 'swipe_right → prev desktop'

        if delta < -SWIPE_THRESHOLD:
            self._fire('next_desk')
            self.swipe_start_x = x
            self.cooldown = SWIPE_COOLDOWN
            return 'swipe_left → next desktop'

        return None

    # ─────────────────────────── Fist vertical ───────────────────────────

    def handle_fist_move(self, fist_tip, is_fist):
        """
        Fist moving up   → maximize window
        Fist moving down → minimize window
        """
        if not is_fist or fist_tip is None:
            self.fist_start_y = None
            self.fist_frames  = 0
            return None

        _, y = fist_tip
        self.fist_frames += 1

        if self.fist_start_y is None:
            self.fist_start_y = y
            return None

        # Need at least 10 frames holding fist before checking
        if self.fist_frames < 10:
            return None

        delta = y - self.fist_start_y

        if delta < -80:
            self._fire('fullscreen')
            self.fist_start_y = y
            self.fist_frames  = 0
            return 'fist up → maximize'

        if delta > 80:
            self._fire('minimize')
            self.fist_start_y = y
            self.fist_frames  = 0
            return 'fist down → minimize'

        return None

    # ─────────────────────────── Quick actions ───────────────────────────

    def show_desktop(self):
        self._fire('desktop')

    def task_view(self):
        self._fire('task_view')

    def alt_tab(self):
        self._fire('alt_tab')

    # ─────────────────────────── Internal ───────────────────────────

    def _fire(self, action):
        shortcut = SHORTCUT_MAP.get(action)
        if shortcut:
            keyboard.send(shortcut)