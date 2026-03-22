import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.observations = []
        self.trained = False

    def _vectorize(self, action: dict) -> list:
        action_str = str(action)
        return [
            len(action_str),
            action_str.count("delete"),
            action_str.count("file"),
            action_str.count("email"),
            action_str.count("http"),
            action_str.count("exec"),
            action_str.count("drop"),
            action_str.count("transfer")
        ]

    def observe(self, action: dict):
        vector = self._vectorize(action)
        self.observations.append(vector)

        # Train after 20 observations
        if len(self.observations) >= 20 and not self.trained:
            self.train()

    def train(self):
        X = np.array(self.observations)
        self.model.fit(X)
        self.trained = True
        print("[Thinguva Sentinel] Anomaly detector trained")

    def is_anomaly(self, action: dict) -> bool:
        if not self.trained:
            return False
        vector = np.array([self._vectorize(action)])
        prediction = self.model.predict(vector)
        return prediction[0] == -1