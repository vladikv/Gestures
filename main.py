import time
import cv2
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from controllers.mouse import MouseController
from controllers.windows import WindowsController
from controllers.media import MediaController
from controllers.shortcuts import ShortcutsController
from controllers.air_keyboard import AirKeyboard
from controllers.finger_numbers import FingerNumbers
from ui.overlay import Overlay
from config import CAM_WIDTH, CAM_HEIGHT, GESTURE_HOLD_FRAMES

# ─────────────────────────── Modes ───────────────────────────
MODE_MOUSE    = 'mouse'
MODE_MEDIA    = 'media'
MODE_WINDOWS  = 'windows'
MODE_KEYBOARD = 'keyboard'
MODE_NUMBERS  = 'numbers'

# Cycle order (Numbers is separate — activated by OK)
MODE_CYCLE = [MODE_MOUSE, MODE_MEDIA, MODE_WINDOWS, MODE_KEYBOARD]

# Mode colors for UI
MODE_COLORS = {
    MODE_MOUSE:    (0, 220, 220),
    MODE_MEDIA:    (0, 180, 255),
    MODE_WINDOWS:  (80, 255, 80),
    MODE_KEYBOARD: (255, 180, 0),
    MODE_NUMBERS:  (180, 0, 255),
}

# Frames needed to hold palm/ok to trigger
PALM_HOLD_NEEDED = 35   # ~1.5 sec at 30fps (switching mode)
OK_HOLD_NEEDED   = 25   # ~1 sec at 30fps (numbers)

MOUSE_BLOCK_GESTURES = {'fist', 'scroll', 'open_palm', 'two_side', 'ok'}


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    tracker      = HandTracker(max_hands=1)
    detector     = GestureDetector()
    mouse        = MouseController()
    windows      = WindowsController()
    media        = MediaController()
    shortcuts    = ShortcutsController()
    air_keyboard = AirKeyboard()
    fin_numbers  = FingerNumbers()
    overlay      = Overlay(CAM_WIDTH, CAM_HEIGHT)

    mode            = MODE_MOUSE
    prev_mode       = None   # mode before numbers
    prev_time       = time.time()
    gesture_counter = {}
    palm_hold       = 0
    ok_hold         = 0

    print("GestureOS started!")
    print("✋ Hold palm  → next mode (Mouse→Media→Windows→Keyboard)")
    print("👌 Hold OK   → Numbers mode (hold OK again to go back)")
    print("Q=quit  S=screenshot")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # ── Hand tracking ──
        all_lm       = tracker.process(frame)
        lm0          = all_lm[0] if all_lm else None
        hand_visible = lm0 is not None

        raw_gesture = detector.get_gesture(lm0)
        index_tip   = detector.get_index_tip(lm0)
        pinch_dist  = detector.get_pinch_distance(lm0)
        fingers     = detector.get_fingers_up(lm0)
        wrist       = detector.get_wrist(lm0)

        # ── Gesture stabilization ──
        gesture_counter[raw_gesture] = gesture_counter.get(raw_gesture, 0) + 1
        for g in list(gesture_counter):
            if g != raw_gesture:
                gesture_counter[g] = 0
        gesture = (raw_gesture
                   if gesture_counter.get(raw_gesture, 0) >= GESTURE_HOLD_FRAMES
                   else 'unknown')

        # ── PALM hold → cycle mode ──
        if raw_gesture == 'open_palm' and mode != MODE_NUMBERS:
            palm_hold += 1
        else:
            palm_hold = 0

        if palm_hold == PALM_HOLD_NEEDED:
            current_idx = MODE_CYCLE.index(mode) if mode in MODE_CYCLE else 0
            next_idx    = (current_idx + 1) % len(MODE_CYCLE)
            mode        = MODE_CYCLE[next_idx]
            overlay.notify(f'{mode.upper()} MODE')
            palm_hold = 0

        # ── OK hold → toggle numbers mode ──
        if raw_gesture == 'ok':
            ok_hold += 1
        else:
            ok_hold = 0

        if ok_hold == OK_HOLD_NEEDED:
            if mode == MODE_NUMBERS:
                mode = prev_mode or MODE_MOUSE
                overlay.notify(f'{mode.upper()} MODE')
            else:
                prev_mode = mode
                mode      = MODE_NUMBERS
                overlay.notify('NUMBERS MODE — show fingers!')
            ok_hold = 0

        # ── Draw hold progress indicators ──
        if palm_hold > 0 and wrist:
            _draw_hold_ring(frame, wrist, palm_hold / PALM_HOLD_NEEDED,
                            (0, 255, 180), 'MODE')
        if ok_hold > 0 and wrist:
            _draw_hold_ring(frame, wrist, ok_hold / OK_HOLD_NEEDED,
                            (180, 0, 255), 'OK')

        # ── Tick cooldowns ──
        media.tick()
        shortcuts.tick()

        # ─────────────── MODE: MOUSE ───────────────
        if mode == MODE_MOUSE:
            if hand_visible and gesture not in MOUSE_BLOCK_GESTURES:
                mouse.move(index_tip)

            if gesture == 'scroll':
                mouse.stop_drag()
                mouse.scroll(index_tip)
            elif gesture == 'fist':
                mouse.reset_scroll()
                mouse.start_drag()
            elif gesture == 'two_side':
                mouse.stop_drag()
                mouse.reset_scroll()
                shortcuts.screenshot()
                overlay.notify('Screenshot!')
            else:
                if gesture != 'scroll':
                    mouse.reset_scroll()
                if gesture not in ('fist',):
                    mouse.stop_drag()

            if not mouse.dragging:
                mouse.handle_pinch(pinch_dist)

        # ─────────────── MODE: MEDIA ───────────────
        elif mode == MODE_MEDIA:
            if gesture == 'draw':
                media.volume_up()
                overlay.notify('Volume +')
            elif gesture == 'pinky':
                media.volume_down()
                overlay.notify('Volume -')
            elif gesture == 'fist':
                media.play_pause()
                overlay.notify('Play / Pause')
            elif gesture == 'three':
                media.next_track()
                overlay.notify('Next Track ▶▶')
            elif gesture == 'rock':
                media.prev_track()
                overlay.notify('◀◀ Prev Track')

            _draw_media_hints(frame)

        # ─────────────── MODE: WINDOWS ───────────────
        elif mode == MODE_WINDOWS:
            if gesture == 'fist':
                result = windows.handle_fist_move(wrist, True)
                if result:
                    overlay.notify(result)
            elif gesture == 'two_side':
                windows.alt_tab()
                overlay.notify('Alt + Tab')
            elif raw_gesture == 'open_palm' and palm_hold == 0:
                # swipe only when palm is NOT being held for mode switch
                result = windows.handle_swipe(wrist)
                if result:
                    overlay.notify(result)
            else:
                windows.handle_fist_move(None, False)

        # ─────────────── MODE: KEYBOARD ───────────────
        elif mode == MODE_KEYBOARD:
            pressed = air_keyboard.update(index_tip, pinch_dist)
            if pressed:
                overlay.notify(f'Pressed: {pressed}', duration=20)
            frame = air_keyboard.draw(frame, index_tip, pinch_dist)

        # ─────────────── MODE: NUMBERS ───────────────
        elif mode == MODE_NUMBERS:
            count, fired = fin_numbers.update(fingers)
            if fired:
                overlay.notify(f'Tab {count}  (Ctrl+{count})')
            _draw_number_ui(frame, count, fin_numbers.progress())

        # ── Hand skeleton ──
        if mode != MODE_KEYBOARD:
            tracker.draw(frame)

        # ── UI ──
        _draw_mode_badge(frame, mode, MODE_COLORS[mode])
        frame = overlay.draw(frame, gesture, mode, media)

        # ── FPS ──
        now  = time.time()
        fps  = 1.0 / max(now - prev_time, 1e-9)
        prev_time = now
        overlay.draw_fps(frame, fps)

        cv2.imshow('GestureOS', frame)

        # ── Keyboard shortcuts (fallback) ──
        key = cv2.waitKey(1) & 0xFF
        if   key == ord('q') or key == 27: break
        elif key == ord('1'):
            mode = MODE_MOUSE
            overlay.notify('Mouse Mode')
        elif key == ord('2'):
            mode = MODE_MEDIA
            overlay.notify('Media Mode')
        elif key == ord('3'):
            mode = MODE_WINDOWS
            overlay.notify('Windows Mode')
        elif key == ord('4'):
            mode = MODE_KEYBOARD
            air_keyboard.clear_text()
            overlay.notify('Air Keyboard')
        elif key == ord('5'):
            prev_mode = mode
            mode      = MODE_NUMBERS
            overlay.notify('Finger Numbers')
        elif key == ord('s'):
            shortcuts.screenshot()
            overlay.notify('Screenshot!')

    cap.release()
    cv2.destroyAllWindows()


# ─────────────────────────── Helper UI ───────────────────────────

def _draw_mode_badge(frame, mode, color):
    """Large mode label in top-left"""
    cv2.putText(frame, mode.upper(), (14, 42),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)


def _draw_hold_ring(frame, wrist, progress, color, label):
    """Animated ring near wrist showing hold progress"""
    cx = wrist[0]
    cy = wrist[1] + 55
    angle = int(360 * min(progress, 1.0))
    cv2.ellipse(frame, (cx, cy), (26, 26), -90, 0, angle, color, 3)
    cv2.putText(frame, label, (cx - 14, cy + 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)


def _draw_media_hints(frame):
    hints = [
        '☝  index  =  Vol +',
        '🤙  pinky  =  Vol -',
        '✊  fist   =  Play/Pause',
        '☞☞☞ three =  Next track',
        '🤘  rock   =  Prev track',
    ]
    for i, text in enumerate(hints):
        cv2.putText(frame, text, (20, 100 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 220, 255), 1)


def _draw_number_ui(frame, count, progress):
    h, w   = frame.shape[:2]
    cx, cy = w // 2, h // 2

    label = str(count) if count > 0 else '-'
    cv2.putText(frame, label, (cx - 30, cy + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 200), 4)

    if count > 0 and progress > 0:
        cv2.ellipse(frame, (cx, cy), (70, 70), -90, 0,
                    int(360 * progress), (0, 220, 255), 4)

    cv2.putText(frame, 'Hold still to switch tab  |  OK gesture to exit',
                (cx - 210, cy + 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)


if __name__ == '__main__':
    main()