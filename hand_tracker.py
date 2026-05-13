import cv2
import mediapipe as mp


class HandTracker:
    FINGER_TIPS = [4, 8, 12, 16, 20]

    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands  = mp.solutions.hands
        self.mp_draw   = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        self.results   = None
        self.landmarks = []

    def process(self, frame):
        """
        Process a BGR frame and return list of hand landmarks.
        Each hand is a list of 21 tuples: (x_px, y_px, z_norm)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results   = self.hands.process(rgb)
        self.landmarks = []

        if self.results.multi_hand_landmarks:
            h, w, _ = frame.shape
            for hand_lms in self.results.multi_hand_landmarks:
                points = []
                for lm in hand_lms.landmark:
                    points.append((int(lm.x * w), int(lm.y * h), lm.z))
                self.landmarks.append(points)

        return self.landmarks

    def draw(self, frame):
        """Draw hand skeleton onto frame"""
        if self.results and self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_lms,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style()
                )
        return frame

    def hand_count(self):
        """Number of detected hands in last frame"""
        return len(self.landmarks)