import keyboard
import pyautogui
import time
import threading


class FingerNumbers:
    """
    Detects how many fingers are raised and switches browser tabs.
    1 finger = Ctrl+1, 2 fingers = Ctrl+2, ... 5 fingers = Ctrl+5

    Uses a background thread to send the shortcut so the camera
    window does not need to lose focus.
    """

    COOLDOWN_FRAMES = 45
    STABLE_NEEDED   = 15  # frames finger count must be stable before firing

    def __init__(self):
        self.cooldown     = 0
        self.last_count   = 0
        self.stable_count = 0

    def tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def update(self, fingers):
        """
        Pass fingers list [thumb, index, middle, ring, pinky].
        Returns (count, fired) — fired=True when tab switch triggered.
        """
        self.tick()

        if not fingers:
            self.stable_count = 0
            self.last_count   = 0
            return 0, False

        count = sum(fingers)

        if count < 1 or count > 5:
            self.stable_count = 0
            self.last_count   = 0
            return count, False

        # Stability check
        if count == self.last_count:
            self.stable_count += 1
        else:
            self.stable_count = 0
            self.last_count   = count

        if self.stable_count >= self.STABLE_NEEDED and self.cooldown == 0:
            self._switch_tab(count)
            self.cooldown     = self.COOLDOWN_FRAMES
            self.stable_count = 0
            return count, True

        return count, False

    def _switch_tab(self, number):
        """Fire Ctrl+N in a background thread so camera window keeps focus"""
        def _send():
            # Small delay so user can switch focus to browser if needed
            time.sleep(0.15)
            pyautogui.hotkey('ctrl', str(number))

        threading.Thread(target=_send, daemon=True).start()

    def progress(self):
        """Returns 0.0-1.0 fill for the hold indicator"""
        return min(1.0, self.stable_count / self.STABLE_NEEDED)