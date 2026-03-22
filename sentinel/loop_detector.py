from collections import deque

class LoopDetector:
    def __init__(self, window_size: int = 10, threshold: int = 3):
        self.window_size = window_size
        self.threshold = threshold
        self.history = deque(maxlen=window_size)

    def is_loop(self, action: dict) -> bool:
        action_key = str(action)
        self.history.append(action_key)

        # Count how many times this exact action appeared recently
        count = self.history.count(action_key)
        if count >= self.threshold:
            return True
        return False

    def reset(self):
        self.history.clear()