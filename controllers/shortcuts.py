import keyboard
import pyautogui
import subprocess
from config import SHORTCUT_MAP


class ShortcutsController:
    def __init__(self):
        self.cooldown        = 0
        self.COOLDOWN_FRAMES = 30

    def tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    # ─────────────────────────── Actions ───────────────────────────

    def screenshot(self):
        if not self._ok():
            return
        keyboard.send(SHORTCUT_MAP['screenshot'])
        self._reset()

    def open_explorer(self):
        if not self._ok():
            return
        keyboard.send(SHORTCUT_MAP['explorer'])
        self._reset()

    def open_browser(self):
        if not self._ok():
            return
        # Try to open default browser
        try:
            import webbrowser
            webbrowser.open('https://www.google.com')
        except Exception:
            keyboard.send(SHORTCUT_MAP['browser'])
        self._reset()

    def open_terminal(self):
        if not self._ok():
            return
        try:
            # Windows Terminal or PowerShell
            subprocess.Popen(['wt.exe'])
        except FileNotFoundError:
            try:
                subprocess.Popen(['powershell.exe'])
            except Exception as e:
                print(f"[ShortcutsController] Terminal open failed: {e}")
        self._reset()

    def alt_tab(self):
        if not self._ok():
            return
        keyboard.send(SHORTCUT_MAP['alt_tab'])
        self._reset()

    def fire(self, action_name):
        """Fire any shortcut by name from SHORTCUT_MAP"""
        if not self._ok():
            return
        shortcut = SHORTCUT_MAP.get(action_name)
        if shortcut:
            keyboard.send(shortcut)
            self._reset()

    # ─────────────────────────── Internal ───────────────────────────

    def _ok(self):
        return self.cooldown == 0

    def _reset(self):
        self.cooldown = self.COOLDOWN_FRAMES