"""
Isolation Forest based anomaly detection
Used for detecting fraudulent or unusual transactions
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestDetector:

    def __init__(self, contamination=0.02):
        """
        contamination = expected fraud percentage
        """
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )

    def train(self, data):
        """
        Train model on transaction feature data
        """
        self.model.fit(data)

    def predict(self, transaction_features):
        """
        Predict anomaly for a new transaction
        Returns:
        -1 : anomaly (fraud)
         1 : normal
        """

        prediction = self.model.predict([transaction_features])[0]

        if prediction == -1:
            return "ANOMALY"

        return "NORMAL"

    def anomaly_score(self, transaction_features):
        """
        Calculate anomaly score
        """

        score = self.model.decision_function([transaction_features])[0]

        return float(score)


# Example usage
if __name__ == "__main__":

    # Example transaction dataset
    X = np.array([
        [100],
        [200],
        [150],
        [180],
        [120],
        [50000]  # anomaly example
    ])

    detector = IsolationForestDetector()

    detector.train(X)

    result = detector.predict([50000])

    print("Prediction:", result)