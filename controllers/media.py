import pyautogui
import threading
import time


class MediaController:
    """
    Controls media and volume using keyboard hotkeys via pyautogui.
    Works on Windows without pycaw — uses native volume keys.
    """

    COOLDOWN_FRAMES = 18

    def __init__(self):
        self.cooldown = 0

    def tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    # ─────────────────────────── Volume ───────────────────────────

    def volume_up(self):
        if not self._ok():
            return
        self._send(lambda: pyautogui.press('volumeup'))
        self._reset()

    def volume_down(self):
        if not self._ok():
            return
        self._send(lambda: pyautogui.press('volumedown'))
        self._reset()

    def get_volume(self):
        """Try to get volume via pycaw, return None if unavailable"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices   = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_,
                                         CLSCTX_ALL, None)
            volume    = cast(interface, POINTER(IAudioEndpointVolume))
            return volume.GetMasterVolumeLevelScalar()
        except Exception:
            return None

    # ─────────────────────────── Playback ───────────────────────────

    def play_pause(self):
        if not self._ok():
            return
        self._send(lambda: pyautogui.press('playpause'))
        self._reset()

    def next_track(self):
        if not self._ok():
            return
        self._send(lambda: pyautogui.press('nexttrack'))
        self._reset()

    def prev_track(self):
        if not self._ok():
            return
        self._send(lambda: pyautogui.press('prevtrack'))
        self._reset()

    # ─────────────────────────── Internal ───────────────────────────

    def _ok(self):
        return self.cooldown == 0

    def _reset(self):
        self.cooldown = self.COOLDOWN_FRAMES

    def _send(self, fn):
        """Send hotkey in background thread so camera stays smooth"""
        threading.Thread(target=fn, daemon=True).start()