# ─────────────────────────── Screen ───────────────────────────
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080

# Camera resolution
CAM_WIDTH  = 1280
CAM_HEIGHT = 720

# ─────────────────────────── Smoothing ───────────────────────────
# Mouse movement smoothing (higher = smoother but slower)
MOUSE_SMOOTHING = 3
SCROLL_SENSITIVITY = 2  

# How many frames a gesture must be held before triggering
GESTURE_HOLD_FRAMES = 8

# ─────────────────────────── Mouse ───────────────────────────
# Pinch distance threshold to trigger click
PINCH_CLICK_THRESHOLD = 35

# Dead zone — ignore tiny hand movements (pixels)
MOUSE_DEAD_ZONE = 8

# ─────────────────────────── Swipe ───────────────────────────
# Minimum horizontal movement (px) to count as a swipe
SWIPE_THRESHOLD = 120

# Frames to ignore after a swipe fires (cooldown)
SWIPE_COOLDOWN = 25

# ─────────────────────────── Volume ───────────────────────────
# How much volume changes per gesture trigger (0.0 – 1.0)
VOLUME_STEP = 0.05

# ─────────────────────────── Gestures ───────────────────────────
# Map finger pattern [thumb,index,middle,ring,pinky] → action name
GESTURE_MAP = {
    (0, 1, 0, 0, 0): 'mouse',        # index only      → move mouse
    (0, 1, 1, 0, 0): 'scroll',       # index+middle     → scroll
    (0, 0, 0, 0, 0): 'fist',         # fist             → drag / pause media
    (1, 1, 1, 1, 1): 'open_palm',    # open palm        → swipe / show desktop
    (1, 0, 0, 0, 0): 'thumb_up',     # thumb only up    → volume up
    (0, 0, 0, 0, 1): 'pinky',        # pinky only       → volume down
    (0, 1, 1, 1, 0): 'three',        # index+mid+ring   → next track
    (1, 1, 0, 0, 1): 'rock',         # thumb+idx+pinky  → prev track
    (0, 1, 0, 0, 1): 'two_side',     # index+pinky      → screenshot
}

# ─────────────────────────── Shortcuts ───────────────────────────
SHORTCUT_MAP = {
    'browser':   'ctrl+shift+b',   # open bookmark bar (Chrome/Edge)
    'explorer':  'win+e',          # file explorer
    'terminal':  'ctrl+alt+t',     # terminal (works on some systems)
    'task_view': 'win+tab',        # task / virtual desktops view
    'desktop':   'win+d',          # show desktop
    'fullscreen': 'win+up',        # maximize window
    'minimize':  'win+down',       # minimize window
    'next_desk': 'ctrl+win+right', # next virtual desktop
    'prev_desk': 'ctrl+win+left',  # previous virtual desktop
    'alt_tab':   'alt+tab',        # switch windows
    'screenshot':'win+shift+s',    # snipping tool
}