import numpy as np


class GestureDetector:
    """
    Converts raw hand landmarks from HandTracker into named gestures.
    Stateless — pass landmarks every frame, get a gesture string back.
    """

    FINGER_TIPS = [4, 8, 12, 16, 20]

    # ─────────────────────────── Fingers ───────────────────────────

    def get_fingers_up(self, landmarks):
        """
        Returns [thumb, index, middle, ring, pinky]
        1 = raised, 0 = folded
        Returns [] if no landmarks provided.
        """
        if not landmarks:
            return []

        lm = landmarks
        fingers = []

        # Thumb — compare X axis (mirrored camera)
        fingers.append(1 if lm[4][0] < lm[3][0] else 0)

        # Index, middle, ring, pinky — compare Y axis
        for tip_id in self.FINGER_TIPS[1:]:
            fingers.append(1 if lm[tip_id][1] < lm[tip_id - 2][1] else 0)

        return fingers

    # ─────────────────────────── Gesture ───────────────────────────

    def get_gesture(self, landmarks):
        """
        Returns gesture name string:

        'draw'      — index finger only
        'scroll'    — index + middle
        'fist'      — all fingers folded
        'open_palm' — all fingers raised
        'thumb_up'  — thumb only
        'pinky'     — pinky only
        'three'     — index + middle + ring
        'rock'      — thumb + index + pinky
        'two_side'  — index + pinky
        'pinch'     — thumb and index closer than threshold
        'ok'        — thumb + index form circle, others raised
        'unknown'   — anything else
        """
        if not landmarks:
            return 'unknown'

        fingers = self.get_fingers_up(landmarks)
        if not fingers:
            return 'unknown'

        total = sum(fingers)

        if total == 0:
            return 'fist'

        if total == 5:
            return 'open_palm'

        if fingers == [0, 1, 0, 0, 0]:
            return 'draw'

        if fingers == [0, 1, 1, 0, 0]:
            return 'scroll'

        if fingers == [1, 0, 0, 0, 0]:
            return 'thumb_up'

        if fingers == [0, 0, 0, 0, 1]:
            return 'pinky'

        if fingers == [0, 1, 1, 1, 0]:
            return 'three'

        if fingers == [1, 1, 0, 0, 1]:
            return 'rock'

        if fingers == [0, 1, 0, 0, 1]:
            return 'two_side'

        # OK — thumb tip close to index tip + middle/ring/pinky raised
        if fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            if self._pinch_distance(landmarks) < 40:
                return 'ok'

        # Pinch — thumb and index close, other fingers not checked
        if self._pinch_distance(landmarks) < 40:
            return 'pinch'

        return 'unknown'

    # ─────────────────────────── Distances ───────────────────────────

    def _pinch_distance(self, landmarks):
        thumb = np.array(landmarks[4][:2])
        index = np.array(landmarks[8][:2])
        return float(np.linalg.norm(thumb - index))

    def get_pinch_distance(self, landmarks):
        """Public: distance between thumb and index fingertips"""
        if not landmarks:
            return None
        return self._pinch_distance(landmarks)

    def get_two_hand_distance(self, lm_a, lm_b):
        """Distance between index fingertips of two hands"""
        if not lm_a or not lm_b:
            return None
        p1 = np.array(lm_a[8][:2])
        p2 = np.array(lm_b[8][:2])
        return float(np.linalg.norm(p1 - p2))

    # ─────────────────────────── Tips ───────────────────────────

    def get_index_tip(self, landmarks):
        """Returns (x, y) of index fingertip, or None"""
        if not landmarks:
            return None
        return landmarks[8][:2]

    def get_wrist(self, landmarks):
        """Returns (x, y) of wrist, or None"""
        if not landmarks:
            return None
        return landmarks[0][:2]